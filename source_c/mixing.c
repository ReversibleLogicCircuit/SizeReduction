#include "mixing.h"
/* build_cbits 가 만드는 후보쌍 최대 개수 = (n-1)^2, n<=MAXN(16) => 225. 여유로 256. */
#define MIX_MAX_PAIRS 256
#include <string.h>
#include <stdlib.h>

#define ABS(x) ((x) < 0 ? -(x) : (x))

/* 정적 작업 버퍼 (호출 순차적이라 안전) */
static perm_t   mb_a[MAX_PERM], mb_b[MAX_PERM], mb_c[MAX_PERM];
static option_t mb_opt[MAX_PERM / 2];
static gate_t   mb_g1[LEAF_MAX_GEN], mb_g2[LEAF_MAX_GEN];

static int wanna_cb(int n) { return (n > 2) ? (1 << (n - 2)) : 2; }
/* 최적화: parity==2(=collision) 쌍 수만 필요하므로 option 배열을 채우지 않고
 * inv 만 만들어 직접 센다. (return_options 와 동일 값) */
static int count2(int n, const perm_t *sbox) {
    static int inv[MAX_PERM];
    const int len = 1 << n;
    for (int i = 0; i < len; i++) inv[sbox[i]] = i;
    int c = 0;
    for (int i = 0; i < len; i += 2) if ((inv[i] & 1) == (inv[i + 1] & 1)) c++;
    return c;
}
static int find_val(const perm_t *a, int len, perm_t v) {
    for (int i = 0; i < len; i++) if (a[i] == v) return i;
    return -1;
}

/* ===== 공통 fallback (bestDiff==2 인 경우의 보정 블록) =====
 * gate_out 에 보정 게이트를 채우고 1 반환(있으면). targets 는 bestGates 적용 후 sbox 기준. */
static int mix_fallback_gate(int n, const perm_t *sbox, const gate_t *bestGates, int nb, gate_t *gate_out) {
    memcpy(mb_b, sbox, (size_t)(1 << n) * sizeof(perm_t));
    for (int k = 0; k < nb; k++) apply_gate(n, mb_b, &bestGates[k]);
    int m = return_options(n, mb_b, mb_opt);
    int c2 = 0; for (int i = 0; i < m; i++) if (mb_opt[i].parity == 2) c2++;
    int wanna = wanna_cb(n);
    static char intgt[MAX_PERM];
    memset(intgt, 0, (size_t)(1 << n));
    if (c2 < wanna) { for (int i = 0; i < m; i++) if (mb_opt[i].parity != 2) { intgt[mb_opt[i].v0] = 1; intgt[mb_opt[i].v1] = 1; } }
    else            { for (int i = 0; i < m; i++) if (mb_opt[i].parity == 2) { intgt[mb_opt[i].v0] = 1; intgt[mb_opt[i].v1] = 1; } }
    for (int i = 0; i < (1 << n); i += 2) {
        if (intgt[sbox[i]] && intgt[sbox[i+1]]) {
            gate_init(gate_out, n - n);
            for (int j = n - 1; j >= 1; j--) gate_add_ctrl(gate_out, j, (i >> j) & 1);
            return 1;
        }
    }
    return 0;
}

/* ===== alg_mixing 재귀 탐색 컨텍스트 ===== */
typedef struct {
    int n, wanna, bestDiff, n_best, n_result, found;
    const perm_t *sbox;
    gate_t bestGates[16];
    gate_t result[16];
} amix_t;

/* 최종 게이트(타깃 마지막비트, 제어 i)로 마무리 시도 */
static int amix_try_final(amix_t *c, int i, const perm_t *tSbox, const gate_t *tempGates, int rd) {
    for (int val = 0; val < 2; val++) {
        memcpy(mb_b, tSbox, (size_t)(1 << c->n) * sizeof(perm_t));
        gate_t fg; gate_init(&fg, c->n - c->n); gate_add_ctrl(&fg, c->n - i, val);
        apply_gate(c->n, mb_b, &fg);
        int cnt2 = count2(c->n, mb_b);
        int diff = ABS(c->wanna - cnt2);
        if (cnt2 == c->wanna) {
            for (int k = 0; k < rd; k++) c->result[k] = tempGates[k];
            c->result[rd] = fg; c->n_result = rd + 1; c->found = 1; return 1;
        } else if (c->bestDiff < diff) {
            c->bestDiff = diff;
            for (int k = 0; k < rd; k++) c->bestGates[k] = tempGates[k];
            c->bestGates[rd] = fg; c->n_best = rd + 1;
        }
    }
    return 0;
}

/* permutations(pairs, rd) 재귀 열거 후 vals 적용 */
static int amix_perm(amix_t *c, int i, const int pairs[][2], int m, int rd,
                     int *sel, char *used, int pos) {
    if (pos == rd) {
        for (int vals = 0; vals < (1 << rd); vals++) {
            memcpy(mb_a, c->sbox, (size_t)(1 << c->n) * sizeof(perm_t));
            gate_t tempGates[8];
            for (int j = 0; j < rd; j++) {
                int a = pairs[sel[j]][0], b = pairs[sel[j]][1];
                gate_init(&tempGates[j], c->n - b);
                gate_add_ctrl(&tempGates[j], c->n - a, (vals >> j) & 1);
                apply_gate(c->n, mb_a, &tempGates[j]);
            }
            if (amix_try_final(c, i, mb_a, tempGates, rd)) return 1;
        }
        return 0;
    }
    for (int k = 0; k < m; k++) {
        if (used[k]) continue;
        used[k] = 1; sel[pos] = k;
        if (amix_perm(c, i, pairs, m, rd, sel, used, pos + 1)) return 1;
        used[k] = 0;
    }
    return 0;
}

/* range(1,n+1) 의 2-permutation 중 c[1]!=n 인 쌍 목록 생성 */
static int build_cbits(int n, int pairs[][2]) {
    int m = 0;
    for (int a = 1; a <= n; a++)
        for (int b = 1; b <= n; b++) {
            if (a == b) continue;
            if (b == n) continue;
            pairs[m][0] = a; pairs[m][1] = b; m++;
        }
    return m;
}

int alg_mixing(int n, const perm_t *sbox, gate_t *out) {
    amix_t c; c.n = n; c.wanna = wanna_cb(n); c.sbox = sbox;
    c.found = 0; c.n_best = 0; c.n_result = 0;
    int c2 = count2(n, sbox);
    c.bestDiff = ABS(c.wanna - c2);
    if (c2 == c.wanna) return 0;

    /* restDepth = 0 */
    for (int i = 1; i < n - 1; i++) {
        for (int val = 0; val < 2; val++) {
            memcpy(mb_a, sbox, (size_t)(1 << n) * sizeof(perm_t));
            gate_t g; gate_init(&g, n - n); gate_add_ctrl(&g, n - i, val);
            apply_gate(n, mb_a, &g);
            int cnt2 = count2(n, mb_a);
            int diff = ABS(c.wanna - cnt2);
            if (cnt2 == c.wanna) { out[0] = g; return 1; }
            else if (c.bestDiff < diff) { c.bestDiff = diff; c.bestGates[0] = g; c.n_best = 1; }
        }
    }

    /* restDepth = 1..4 */
    static int pairs[MIX_MAX_PAIRS][2];
    int m = build_cbits(n, pairs);
    int sel[8]; char used[MIX_MAX_PAIRS];
    for (int restDepth = 1; restDepth < 5; restDepth++) {
        for (int i = 1; i < n - 1; i++) {
            memset(used, 0, (size_t)m);
            if (amix_perm(&c, i, pairs, m, restDepth, sel, used, 0)) {
                for (int k = 0; k < c.n_result; k++) out[k] = c.result[k];
                return c.n_result;
            }
        }
    }

    /* fallback */
    if (c.bestDiff == 2) {
        gate_t fg;
        if (mix_fallback_gate(n, sbox, c.bestGates, c.n_best, &fg)) {
            memcpy(mb_b, sbox, (size_t)(1 << n) * sizeof(perm_t));
            for (int k = 0; k < c.n_best; k++) apply_gate(n, mb_b, &c.bestGates[k]);
            apply_gate(n, mb_b, &fg);
            if (count2(n, mb_b) == c.wanna) {
                int k = 0; for (; k < c.n_best; k++) out[k] = c.bestGates[k];
                out[k++] = fg; return k;
            }
        }
    }
    return alg_mixing_more(n, sbox, out);
}

/* ===== newMixing ===== */
static int nm_update_or_done(int n, int wanna, int *bestDiff, gate_t *best, int *nbest,
                             const perm_t *tSbox, const gate_t *gs, int ng,
                             gate_t *out, int *done) {
    int cnt2 = count2(n, tSbox);
    int diff = ABS(wanna - cnt2);
    if (cnt2 == wanna) { for (int k = 0; k < ng; k++) out[k] = gs[k]; *done = ng; return 1; }
    else if (*bestDiff < diff) { *bestDiff = diff; for (int k = 0; k < ng; k++) best[k] = gs[k]; *nbest = ng; }
    return 0;
}

int new_mixing(int n, const perm_t *sbox, gate_t *out) {
    int wanna = wanna_cb(n);
    int c2 = count2(n, sbox);
    int bestDiff = ABS(wanna - c2);
    gate_t best[4]; int nbest = 0;
    if (c2 == wanna) return 0;
    int done;

    int n2 = cn_last_target_gates(n, mb_g2);
    for (int x = 0; x < n2; x++) {
        memcpy(mb_a, sbox, (size_t)(1 << n) * sizeof(perm_t));
        apply_gate(n, mb_a, &mb_g2[x]);
        gate_t gs[1] = { mb_g2[x] };
        if (nm_update_or_done(n, wanna, &bestDiff, best, &nbest, mb_a, gs, 1, out, &done)) return done;
    }
    int n1 = cn_gates(n, mb_g1);
    /* C C : product(CNGates, CN_LastTargetGates) */
    for (int x = 0; x < n1; x++) for (int y = 0; y < n2; y++) {
        if (gate_eq(&mb_g1[x], &mb_g2[y])) continue;
        memcpy(mb_a, sbox, (size_t)(1 << n) * sizeof(perm_t));
        apply_gate(n, mb_a, &mb_g1[x]); apply_gate(n, mb_a, &mb_g2[y]);
        gate_t gs[2] = { mb_g1[x], mb_g2[y] };
        if (nm_update_or_done(n, wanna, &bestDiff, best, &nbest, mb_a, gs, 2, out, &done)) return done;
    }
    /* C C C : product(CNGates, CNGates, CN_LastTargetGates) */
    for (int x = 0; x < n1; x++) for (int y = 0; y < n1; y++) for (int z = 0; z < n2; z++) {
        if (gate_eq(&mb_g1[x], &mb_g1[y]) || gate_eq(&mb_g1[y], &mb_g2[z])) continue;
        memcpy(mb_a, sbox, (size_t)(1 << n) * sizeof(perm_t));
        apply_gate(n, mb_a, &mb_g1[x]); apply_gate(n, mb_a, &mb_g1[y]); apply_gate(n, mb_a, &mb_g2[z]);
        gate_t gs[3] = { mb_g1[x], mb_g1[y], mb_g2[z] };
        if (nm_update_or_done(n, wanna, &bestDiff, best, &nbest, mb_a, gs, 3, out, &done)) return done;
    }
    /* C T : product(CNGates, Tof_LastTargetGates) */
    int nt2 = tof_last_target_gates(n, mb_g2);
    for (int x = 0; x < n1; x++) for (int y = 0; y < nt2; y++) {
        memcpy(mb_a, sbox, (size_t)(1 << n) * sizeof(perm_t));
        apply_gate(n, mb_a, &mb_g1[x]); apply_gate(n, mb_a, &mb_g2[y]);
        gate_t gs[2] = { mb_g1[x], mb_g2[y] };
        if (nm_update_or_done(n, wanna, &bestDiff, best, &nbest, mb_a, gs, 2, out, &done)) return done;
    }
    /* T C : product(TofGates, CN_LastTargetGates) */
    int nt1 = tof_gates(n, mb_g1);
    n2 = cn_last_target_gates(n, mb_g2);
    for (int x = 0; x < nt1; x++) for (int y = 0; y < n2; y++) {
        memcpy(mb_a, sbox, (size_t)(1 << n) * sizeof(perm_t));
        apply_gate(n, mb_a, &mb_g1[x]); apply_gate(n, mb_a, &mb_g2[y]);
        gate_t gs[2] = { mb_g1[x], mb_g2[y] };
        if (nm_update_or_done(n, wanna, &bestDiff, best, &nbest, mb_a, gs, 2, out, &done)) return done;
    }
    /* fallback */
    if (bestDiff == 2) {
        gate_t fg;
        if (mix_fallback_gate(n, sbox, best, nbest, &fg)) {
            memcpy(mb_b, sbox, (size_t)(1 << n) * sizeof(perm_t));
            for (int k = 0; k < nbest; k++) apply_gate(n, mb_b, &best[k]);
            apply_gate(n, mb_b, &fg);
            if (count2(n, mb_b) == wanna) {
                int k = 0; for (; k < nbest; k++) out[k] = best[k];
                out[k++] = fg; return k;
            }
        }
    }
    return 0;
}

/* ===== alg_mixingMore (버그 포함 충실 포팅) ===== */
static perm_t am_tSbox[MAX_PERM], am_ttSbox[MAX_PERM], am_ttt[MAX_PERM];
static int comb2(int n, int *arr, int m, int pairs[][2]) {  /* combinations(arr[0..m-1],2) */
    (void)n; int k = 0;
    for (int a = 0; a < m; a++) for (int b = a + 1; b < m; b++) { pairs[k][0] = arr[a]; pairs[k][1] = arr[b]; k++; }
    return k;
}
typedef struct { int n, wanna, bestDiff, n_best, n_result, found; gate_t bestGates[16], result[16]; } ammore_t;

static int ammore_perm(ammore_t *c, int i, const gate_t *firstGate, const int pairs[][2], int m,
                       int rd, int *sel, char *used, int pos) {
    if (pos == rd) {
        for (int vals = 0; vals < (1 << rd); vals++) {
            memcpy(am_ttSbox, am_tSbox, (size_t)(1 << c->n) * sizeof(perm_t));   /* deepcopy(tSbox) */
            gate_t tempGates[8];
            for (int j = 0; j < rd; j++) {
                int a = pairs[sel[j]][0], b = pairs[sel[j]][1];
                gate_init(&tempGates[j], c->n - b);
                gate_add_ctrl(&tempGates[j], c->n - a, (vals >> j) & 1);
                /* BUG 재현: tSbox = apply_gate(ttSbox, gateMiddle) (ttSbox 불변, tSbox 덮어씀) */
                memcpy(am_tSbox, am_ttSbox, (size_t)(1 << c->n) * sizeof(perm_t));
                apply_gate(c->n, am_tSbox, &tempGates[j]);
            }
            for (int val = 0; val < 2; val++) {
                memcpy(am_ttt, am_ttSbox, (size_t)(1 << c->n) * sizeof(perm_t));
                gate_t gl; gate_init(&gl, c->n - c->n); gate_add_ctrl(&gl, c->n - i, val);
                apply_gate(c->n, am_ttt, &gl);
                int cnt2 = count2(c->n, am_ttt);
                int diff = ABS(c->wanna - cnt2);
                if (cnt2 == c->wanna) {
                    int k = 0; c->result[k++] = *firstGate;
                    for (int t = 0; t < rd; t++) c->result[k++] = tempGates[t];
                    c->result[k++] = gl; c->n_result = k; c->found = 1; return 1;
                } else if (c->bestDiff < diff) {
                    c->bestDiff = diff; int k = 0; c->bestGates[k++] = *firstGate;
                    for (int t = 0; t < rd; t++) c->bestGates[k++] = tempGates[t];
                    c->bestGates[k++] = gl; c->n_best = k;
                }
            }
        }
        return 0;
    }
    for (int k = 0; k < m; k++) {
        if (used[k]) continue;
        used[k] = 1; sel[pos] = k;
        if (ammore_perm(c, i, firstGate, pairs, m, rd, sel, used, pos + 1)) return 1;
        used[k] = 0;
    }
    return 0;
}

int alg_mixing_more(int n, const perm_t *sbox, gate_t *out) {
    ammore_t c; c.n = n; c.wanna = wanna_cb(n); c.found = 0; c.n_best = 0; c.n_result = 0;
    int c2 = count2(n, sbox);
    c.bestDiff = ABS(c.wanna - c2);
    if (c2 == c.wanna) return 0;

    static int conCans[MAXN], pairs[256][2];
    /* 1) target = 마지막 비트, 제어 2개 (combinations(range(1,n),2)) */
    int mc = 0; for (int v = 1; v < n; v++) conCans[mc++] = v;
    int np = comb2(n, conCans, mc, pairs);
    const int vv[4][2] = { {0,0},{0,1},{1,0},{1,1} };
    for (int p = 0; p < np; p++) {
        for (int t = 0; t < 4; t++) {
            memcpy(mb_a, sbox, (size_t)(1 << n) * sizeof(perm_t));
            gate_t g; gate_init(&g, n - n);
            gate_add_ctrl(&g, n - pairs[p][0], vv[t][0]);
            gate_add_ctrl(&g, n - pairs[p][1], vv[t][1]);
            apply_gate(n, mb_a, &g);
            int cnt2 = count2(n, mb_a), diff = ABS(c.wanna - cnt2);
            if (cnt2 == c.wanna) { out[0] = g; return 1; }
            else if (c.bestDiff < diff) { c.bestDiff = diff; c.bestGates[0] = g; c.n_best = 1; }
        }
    }

    /* 2) target = i, 제어 2개 + 중간(restDepth) + 마지막 (버그 포함) */
    static int midpairs[64][2]; int sel[8]; char used[MIX_MAX_PAIRS];
    int nmid = build_cbits(n, midpairs);
    for (int i = 1; i < n - 1; i++) {
        mc = 0; for (int v = 1; v < i; v++) conCans[mc++] = v; for (int v = i + 1; v <= n; v++) conCans[mc++] = v;
        np = comb2(n, conCans, mc, pairs);
        for (int p = 0; p < np; p++) {
            for (int t = 0; t < 4; t++) {
                gate_t gate; gate_init(&gate, n - i);
                gate_add_ctrl(&gate, n - pairs[p][0], vv[t][0]);
                gate_add_ctrl(&gate, n - pairs[p][1], vv[t][1]);
                memcpy(am_tSbox, sbox, (size_t)(1 << n) * sizeof(perm_t));
                apply_gate(n, am_tSbox, &gate);   /* tSbox (이후 gates 루프에서 evolve) */
                for (int restDepth = 1; restDepth < 4; restDepth++) {
                    for (int j = 1; j < n - 1; j++) {
                        memset(used, 0, (size_t)nmid);
                        if (ammore_perm(&c, i, &gate, midpairs, nmid, restDepth, sel, used, 0)) {
                            for (int k = 0; k < c.n_result; k++) out[k] = c.result[k];
                            return c.n_result;
                        }
                    }
                }
            }
        }
    }

    /* fallback (alg_mixingMore 는 재확인 없이 bestGates+[gate] 반환) */
    if (c.bestDiff == 2) {
        gate_t fg;
        if (mix_fallback_gate(n, sbox, c.bestGates, c.n_best, &fg)) {
            int k = 0; for (; k < c.n_best; k++) out[k] = c.bestGates[k];
            out[k++] = fg; return k;
        }
    }
    return 0;
}

/* ===== alg_preprocessing ===== */
static int list_remove_val(int *lst, int len, int v) {   /* 첫 v 제거, 새 길이 반환 */
    int pos = -1; for (int i = 0; i < len; i++) if (lst[i] == v) { pos = i; break; }
    if (pos < 0) return len;
    for (int i = pos; i < len - 1; i++) lst[i] = lst[i+1];
    return len - 1;
}

int alg_preprocessing(int n, const perm_t *sbox, gate_t *out) {
    int ng = 0;
    perm_t *tS = mb_c;                                   /* tSbox */
    memcpy(tS, sbox, (size_t)(1 << n) * sizeof(perm_t));

    /* step 1. mixing */
    static gate_t mix[MIX_MAX_GATES];
    int nmix = (n <= 12) ? alg_mixing(n, sbox, mix) : new_mixing(n, sbox, mix);
    for (int k = 0; k < nmix; k++) { apply_gate(n, tS, &mix[k]); out[ng++] = mix[k]; }

    int m = return_options(n, tS, mb_opt);
    int c0 = 0, c1 = 0;
    for (int i = 0; i < m; i++) { if (mb_opt[i].parity == 0) c0++; else if (mb_opt[i].parity == 1) c1++; }
    int evenCB = (c1 > c0) ? ((c1 - c0) >> 1) : 0;
    int oddCB  = (c0 > c1) ? ((c0 - c1) >> 1) : 0;
    int normalCB = (1 << (n - 2)) - (c0 > c1 ? c0 : c1);

    /* step 2-1: LCB/RCB 분류 (collision block) */
    static int LCB[MAX_PERM], RCB[MAX_PERM]; int nL = 0, nR = 0;
    static int inv[MAX_PERM]; perm_build_inv(tS, 1 << n, inv);
    for (int i = 0; i < m; i++) {
        if (mb_opt[i].parity == 2) {
            int v0 = mb_opt[i].v0, v1 = mb_opt[i].v1;
            if (inv[v0] % 2 == 0) { LCB[nL++] = v0; LCB[nL++] = v1; }
            else                  { RCB[nR++] = v0; RCB[nR++] = v1; }
        }
    }

    /* free interrupting block 분석 (1차: 카운트만) */
    static char made[MAX_PERM];
    static char inL[MAX_PERM], inR[MAX_PERM];
    #define REBUILD_INLR() do{ \
        memset(inL,0,(size_t)(1<<n)); memset(inR,0,(size_t)(1<<n)); \
        for(int _i=0;_i<nL;_i++) inL[LCB[_i]]=1; \
        for(int _i=0;_i<nR;_i++) inR[RCB[_i]]=1; \
    }while(0)
    REBUILD_INLR();
    int freeNormal = 0, freeEven = 0, freeOdd = 0;
    memset(made, 0, (size_t)(1 << n));
    for (int i = 0; i < (1 << n); i += 2) {
        perm_t a = tS[i], b = tS[i+1];
        if (inL[a] && inR[b] && !made[a] && !made[b]) {
            int act = 0;
            if ((a & 1) == (b & 1)) { act = 1; freeNormal++; }
            else if ((a & 1) == 0) { act = 1; freeOdd++; }
            else { act = 1; freeEven++; }
            if (act) { made[a]=1; made[a^1]=1; made[b]=1; made[b^1]=1; }
        }
    }
    if (freeEven > evenCB || freeOdd > oddCB || freeNormal > normalCB) {
        while (((freeEven - evenCB > freeOdd - oddCB ? freeEven - evenCB : freeOdd - oddCB) != 0) && normalCB > freeNormal) {
            normalCB -= 2; evenCB += 1; oddCB += 1;
        }
    }
    if (normalCB < 0) { normalCB += 2; evenCB -= 1; oddCB -= 1; }

    /* step 2-2: free block 활성화 + LCB/RCB 제거 */
    static int CBNum[MAX_PERM]; int nCB = 0;
    memset(made, 0, (size_t)(1 << n));
    for (int i = 0; i < (1 << n); i += 2) {
        perm_t a = tS[i], b = tS[i+1];
        if (inL[a] && inR[b] && !made[a] && !made[b]) {
            int act = 0;
            if ((a & 1) == (b & 1)) { if (normalCB > 0) { act = 1; normalCB--; } }
            else if ((a & 1) == 0) { if (oddCB > 0) { act = 1; oddCB--; } }
            else { if (evenCB > 0) { act = 1; evenCB--; } }
            if (act) {
                CBNum[nCB++] = a; CBNum[nCB++] = b;
                made[a]=1; made[a^1]=1; made[b]=1; made[b^1]=1;
                nL = list_remove_val(LCB, nL, a); nL = list_remove_val(LCB, nL, a ^ 1);
                nR = list_remove_val(RCB, nR, b); nR = list_remove_val(RCB, nR, b ^ 1);
                REBUILD_INLR();
            }
        }
    }

    cons_t cons; cons_clear(&cons);
    char np[MAXN + 1];
    /* step 2-3: free block 할당 */
    for (int i = 0; i < nCB; i += 2) {
        int idx1 = find_val(tS, 1 << n, (perm_t)CBNum[i]);
        int idx2 = find_val(tS, 1 << n, (perm_t)CBNum[i+1]);
        gate_t gs[SUB_MAX_GATES]; int ng2 = sub_alloc(n, idx1, idx2, &cons, gs);
        for (int k = 0; k < ng2; k++) { apply_gate(n, tS, &gs[k]); out[ng++] = gs[k]; }
        next_position(n, &cons, np); cons_push(&cons, np); cons_update(n, &cons);
    }

    /* step 3: interrupting block 구성 */
    while (nR != 0) {
        int tr0, tr1;
        perm_build_inv(tS, 1 << n, inv);
        if (oddCB > 0) {
            tr0 = LCB[0]; tr1 = RCB[1];
            int rl = -1, rr = -1;
            for (int i = 0; i < nL; i += 2) if ((inv[LCB[i]] >> (n-2)) != 0) { rl = LCB[i]; break; }
            for (int i = 0; i < nR; i += 2) if ((inv[RCB[i+1]] >> (n-2)) != 0) { rr = RCB[i+1]; break; }
            if (rl >= 0 && rr >= 0) { tr0 = rl; tr1 = rr; }
            oddCB--;
        } else if (evenCB > 0) {
            tr0 = LCB[1]; tr1 = RCB[0];
            int rl = -1, rr = -1;
            for (int i = 0; i < nL; i += 2) if ((inv[LCB[i+1]] >> (n-2)) != 0) { rl = LCB[i+1]; break; }
            for (int i = 0; i < nR; i += 2) if ((inv[RCB[i]] >> (n-2)) != 0) { rr = RCB[i]; break; }
            if (rl >= 0 && rr >= 0) { tr0 = rl; tr1 = rr; }
            evenCB--;
        } else {
            tr0 = LCB[0]; tr1 = RCB[0];
            int rl0=-1,rr0=-1,rl1=-1,rr1=-1;
            for (int i = 0; i < nL; i += 2) if ((inv[LCB[i]]   >> (n-2)) != 0) { rl0 = LCB[i];   break; }
            for (int i = 0; i < nR; i += 2) if ((inv[RCB[i]]   >> (n-2)) != 0) { rr0 = RCB[i];   break; }
            for (int i = 0; i < nL; i += 2) if ((inv[LCB[i+1]] >> (n-2)) != 0) { rl1 = LCB[i+1]; break; }
            for (int i = 0; i < nR; i += 2) if ((inv[RCB[i+1]] >> (n-2)) != 0) { rr1 = RCB[i+1]; break; }
            if (rl0 >= 0 && rr0 >= 0) { tr0 = rl0; tr1 = rr0; }
            else if (rl1 >= 0 && rr1 >= 0) { tr0 = rl1; tr1 = rr1; }
            normalCB--;
        }
        int i1 = find_val(tS, 1 << n, (perm_t)tr0), i2 = find_val(tS, 1 << n, (perm_t)tr1);
        gate_t gs[SUB_MAX_GATES]; int g1 = sub_cons(n, i1, i2, &cons, gs);
        for (int k = 0; k < g1; k++) { apply_gate(n, tS, &gs[k]); out[ng++] = gs[k]; }
        i1 = find_val(tS, 1 << n, (perm_t)tr0); i2 = find_val(tS, 1 << n, (perm_t)tr1);
        int g2 = sub_alloc(n, i1, i2, &cons, gs);
        for (int k = 0; k < g2; k++) { apply_gate(n, tS, &gs[k]); out[ng++] = gs[k]; }
        nL = list_remove_val(LCB, nL, tr0); nL = list_remove_val(LCB, nL, tr0 ^ 1);
        nR = list_remove_val(RCB, nR, tr1); nR = list_remove_val(RCB, nR, tr1 ^ 1);
        next_position(n, &cons, np); cons_push(&cons, np); cons_update(n, &cons);
    }

    /* step 4: 한 개의 Toffoli 로 interrupting block 뒤집기 */
    gate_t fg;
    if (n != 2) { gate_init(&fg, n - n); gate_add_ctrl(&fg, n - 1, 0); gate_add_ctrl(&fg, n - 2, 0); }
    else        { gate_init(&fg, 0); gate_add_ctrl(&fg, 1, 0); }
    out[ng++] = fg; apply_gate(n, tS, &fg);
    return ng;
}
