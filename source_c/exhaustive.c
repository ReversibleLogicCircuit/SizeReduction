#include "exhaustive.h"
#include <string.h>
#include <stdlib.h>

#define DE_MAXLVL (MAX_QUALITY + 2)

static perm_t (*de_sbox)[MAX_PERM];
static int    (*de_nlist)[MAX_PERM];
static cons_t *de_cons;
#pragma omp threadprivate(de_sbox, de_nlist, de_cons)
static void ensure_de(void) {
    if (!de_sbox) {
        de_sbox  = (perm_t (*)[MAX_PERM]) malloc((size_t)DE_MAXLVL * sizeof(*de_sbox));
        de_nlist = (int    (*)[MAX_PERM]) malloc((size_t)DE_MAXLVL * sizeof(*de_nlist));
        de_cons  = (cons_t *)             malloc((size_t)DE_MAXLVL * sizeof(cons_t));
    }
}

static perm_t ml_sbox[MAX_PERM];      /* make_list_* per-option 작업 복사 */
static int    ml_nlist[MAX_PERM];
static cons_t ml_cons;
static perm_t fb_even[MAX_PERM], fb_odd[MAX_PERM];
static int    temp_even[MAX_PERM];
static int    inv_b[MAX_PERM];
#pragma omp threadprivate(ml_sbox, ml_nlist, ml_cons, fb_even, fb_odd, temp_even, inv_b)

static int    inv_a[MAX_PERM];        /* makeList_Half 순차 사전패스 전용(병렬영역 밖) */
static int    half_idx[MAX_PERM];     /* makeList_Half 통과 후보 인덱스(순차 작성, 병렬 읽기) */

/* ---- helpers ---- */
static int is_reduce(const char *s, int tn) {
    if ((int)strlen(s) != tn) return 0;
    if (s[0] != '0') return 0;
    for (int i = 1; i < tn; i++) if (s[i] != '-') return 0;
    return 1;
}
static int isum(const int *a, int d) { int s = 0; for (int i = 0; i < d; i++) s += a[i]; return s; }
static int lexless(const int *a, const int *b, int d) {
    for (int i = 0; i < d; i++) { if (a[i] < b[i]) return 1; if (a[i] > b[i]) return 0; }
    return 0;
}

/* ===== depthExhasutive ===== */
static void depth_exhaustive(int n, int now_n, const perm_t *sbox, int slen,
                             const cons_t *cons, const int *nlist, int nlen,
                             int *nowQ, int *bestQ, int now_d, int d) {
    ensure_de();
    if (now_d == d) {
        int sn = isum(nowQ, d), sb = isum(bestQ, d);
        if ((sn == sb && lexless(nowQ, bestQ, d)) || sn < sb)
            for (int i = 0; i < d; i++) bestQ[i] = nowQ[i];
        return;
    }
    for (int i = 0; i + 1 < nlen; i += 2) {
        int rows[2] = { nlist[i], nlist[i+1] };
        int tNow_n = now_n;
        perm_t *ws = de_sbox[now_d]; int *wn = de_nlist[now_d]; cons_t *wc = &de_cons[now_d];
        memcpy(ws, sbox, (size_t)slen * sizeof(perm_t));
        *wc = *cons;
        memcpy(wn, nlist, (size_t)nlen * sizeof(int));
        int wlen = nlen, wslen = slen, costs[2];
        make_block_semi(n, tNow_n, ws, wslen, wc, wn, &wlen, rows, costs);
        nowQ[now_d] = costs[0] + costs[1];
        if (wc->count >= 1 && is_reduce(wc->s[0], tNow_n) && tNow_n > 2) {
            wc->count = 0; tNow_n--; int nl = 1 << tNow_n;
            memmove(ws, ws + (wslen - nl), (size_t)nl * sizeof(perm_t)); wslen = nl;
        }
        depth_exhaustive(n, tNow_n, ws, wslen, wc, wn, wlen, nowQ, bestQ, now_d + 1, d);
    }
}

/* ===== depthExhasutive2 ===== */
typedef struct { int q[MAX_QUALITY]; int rows[MAX_QUALITY][2]; } d2q_t;
static void d2q_copy(d2q_t *dst, const d2q_t *src, int d) {
    for (int i = 0; i < d; i++) { dst->q[i] = src->q[i]; dst->rows[i][0] = src->rows[i][0]; dst->rows[i][1] = src->rows[i][1]; }
}
static void depth_exhaustive2(int n, int now_n, const perm_t *sbox, int slen,
                              const cons_t *cons, const int *nlist, int nlen,
                              d2q_t *nowQ, d2q_t *bestQ, d2q_t *backupQ, int now_d, int d) {
    ensure_de();
    if (now_d == d) {
        int ne, no;
        fb_list(3, nlist, nlen, sbox, slen, fb_even, &ne, fb_odd, &no);
        int oddEmpty = (no == 0);
        int sn = isum(nowQ->q, d);
        int sb = isum(bestQ->q, d);
        if (oddEmpty && ((sn == sb && lexless(nowQ->q, bestQ->q, d)) || sn < sb)) d2q_copy(bestQ, nowQ, d);
        int sk = isum(backupQ->q, d);
        if ((sn == sk && lexless(nowQ->q, backupQ->q, d)) || sn < sk) d2q_copy(backupQ, nowQ, d);
        return;
    }
    for (int i = 0; i + 1 < nlen; i += 2) {
        int rows[2] = { nlist[i], nlist[i+1] };
        int tNow_n = now_n;
        perm_t *ws = de_sbox[now_d]; int *wn = de_nlist[now_d]; cons_t *wc = &de_cons[now_d];
        memcpy(ws, sbox, (size_t)slen * sizeof(perm_t));
        *wc = *cons;
        memcpy(wn, nlist, (size_t)nlen * sizeof(int));
        int wlen = nlen, wslen = slen, costs[2];
        make_block_semi(n, tNow_n, ws, wslen, wc, wn, &wlen, rows, costs);
        nowQ->q[now_d] = costs[0] + costs[1];
        nowQ->rows[now_d][0] = rows[0]; nowQ->rows[now_d][1] = rows[1];
        if (wc->count >= 1 && is_reduce(wc->s[0], tNow_n) && tNow_n > 2) {
            wc->count = 0; tNow_n--; int nl = 1 << tNow_n;
            memmove(ws, ws + (wslen - nl), (size_t)nl * sizeof(perm_t)); wslen = nl;
        }
        depth_exhaustive2(n, tNow_n, ws, wslen, wc, wn, wlen, nowQ, bestQ, backupQ, now_d + 1, d);
    }
}

/* ===== makeList_Full ===== */
int make_list_full(int n, int now_n, const perm_t *sbox, int slen,
                   const cons_t *cons, const int *nlist, int nlen, int depth, mlopt_t *out) {
    const perm_t *slice = sbox + (slen - (1 << now_n));   /* sbox[-(1<<now_n):] */
    int sl = 1 << now_n;
    int nopt = nlen / 2;                                  /* 후보 수 = 행쌍 수 (순서 보존) */
    #pragma omp parallel for schedule(dynamic)
    for (int ii = 0; ii < nopt; ii++) {
        int i = 2 * ii;
        int nownow_n = now_n;
        mlopt_t *o = &out[ii];
        o->rows[0] = nlist[i]; o->rows[1] = nlist[i+1]; o->nq = 0; o->free_count = 0;
        memcpy(ml_sbox, slice, (size_t)sl * sizeof(perm_t));
        ml_cons = *cons;
        memcpy(ml_nlist, nlist, (size_t)nlen * sizeof(int));
        int wlen = nlen, wslen = sl, costs[2];
        int rows[2] = { nlist[i], nlist[i+1] };
        make_block_semi(n, nownow_n, ml_sbox, wslen, &ml_cons, ml_nlist, &wlen, rows, costs);
        if (ml_cons.count >= 1 && is_reduce(ml_cons.s[0], nownow_n) && nownow_n > 2) {
            ml_cons.count = 0; nownow_n--; int nl = 1 << nownow_n;
            memmove(ml_sbox, ml_sbox + (wslen - nl), (size_t)nl * sizeof(perm_t)); wslen = nl;
        }
        o->quality[o->nq++] = costs[0] + costs[1];
        int ne, no;
        fb_list(nownow_n, ml_nlist, wlen, ml_sbox, wslen, fb_even, &ne, fb_odd, &no);
        int e = ne >> 1, f = no >> 1; o->free_count = (e > f) ? e : f;
        if (depth != 0) {
            int tDepth = depth; if (depth > (wlen >> 1)) tDepth = wlen >> 1;
            int nowQ[MAX_QUALITY], bestQ[MAX_QUALITY];
            for (int j = 0; j < tDepth; j++) { nowQ[j] = 100; bestQ[j] = 100; }
            depth_exhaustive(n, nownow_n, ml_sbox, wslen, &ml_cons, ml_nlist, wlen, nowQ, bestQ, 0, tDepth);
            for (int j = 0; j < tDepth; j++) o->quality[o->nq++] = bestQ[j];
        }
    }
    return nopt;
}

/* ===== makeList2_Full ===== */
int make_list2_full(int n, int now_n, const perm_t *sbox, int slen,
                    const cons_t *cons, const int *nlist, int nlen, int oddflag, int depth, mlopt2_t *out) {
    const perm_t *slice = sbox + (slen - (1 << now_n));
    int sl = 1 << now_n;
    int nopt = nlen / 2;
    #pragma omp parallel for schedule(dynamic)
    for (int ii = 0; ii < nopt; ii++) {
        int i = 2 * ii;
        int nownow_n = now_n;
        int toddFlag = oddflag;
        mlopt2_t *o = &out[ii];
        o->rows[0] = nlist[i]; o->rows[1] = nlist[i+1]; o->nq = 0; o->free_count = 0; o->n_best = 0;
        memcpy(ml_sbox, slice, (size_t)sl * sizeof(perm_t));
        ml_cons = *cons;
        memcpy(ml_nlist, nlist, (size_t)nlen * sizeof(int));
        int wlen = nlen, wslen = sl, costs[2];
        int rows[2] = { nlist[i], nlist[i+1] };
        make_block_semi(n, nownow_n, ml_sbox, wslen, &ml_cons, ml_nlist, &wlen, rows, costs);
        if (ml_cons.count >= 1 && is_reduce(ml_cons.s[0], nownow_n) && nownow_n > 2) {
            ml_cons.count = 0; nownow_n--; int nl = 1 << nownow_n;
            memmove(ml_sbox, ml_sbox + (wslen - nl), (size_t)nl * sizeof(perm_t)); wslen = nl;
            if (costs[0] == 2 * (n - 1) - 3) toddFlag = toddFlag ? 0 : 1;
        }
        o->quality[o->nq++] = costs[0] + costs[1];
        int ne, no;
        fb_list(nownow_n, ml_nlist, wlen, ml_sbox, wslen, fb_even, &ne, fb_odd, &no);
        int e = ne >> 1, f = no >> 1; o->free_count = (e > f) ? e : f;
        if (depth == 0) continue;
        int tDepth = depth; if (depth > (wlen >> 1)) tDepth = wlen >> 1;
        d2q_t nowQ, bestQ, backupQ;
        for (int j = 0; j < tDepth; j++) {
            nowQ.q[j] = 10000; bestQ.q[j] = 10000; backupQ.q[j] = 10000;
            nowQ.rows[j][0] = nowQ.rows[j][1] = 0;
            bestQ.rows[j][0] = bestQ.rows[j][1] = 0;
            backupQ.rows[j][0] = backupQ.rows[j][1] = 0;
        }
        depth_exhaustive2(n, nownow_n, ml_sbox, wslen, &ml_cons, ml_nlist, wlen, &nowQ, &bestQ, &backupQ, 0, tDepth);
        int has10000 = 0; for (int j = 0; j < tDepth; j++) if (bestQ.q[j] == 10000) has10000 = 1;
        if (!has10000) {
            for (int j = 0; j < tDepth; j++) o->quality[o->nq++] = bestQ.q[j];
            o->n_best = tDepth;
            for (int j = 0; j < tDepth; j++) { o->best_rows[j][0] = bestQ.rows[j][0]; o->best_rows[j][1] = bestQ.rows[j][1]; }
            /* 마지막 4 블록 품질 예측 (option 은 이미 추가된 것으로 간주) */
            int last = o->quality[o->nq - 1];
            if (toddFlag && last != 2 * (n - 1) - 3) {
                o->quality[o->nq++] = 2 * (n - 1) - 5; o->quality[o->nq++] = 0;
                o->quality[o->nq++] = 2 * (n - 1) - 3; o->quality[o->nq++] = 0;
            } else {
                o->quality[o->nq++] = 2 * (n - 1) - 5; o->quality[o->nq++] = 0;
                o->quality[o->nq++] = 0; o->quality[o->nq++] = 0;
            }
        } else {
            for (int j = 0; j < tDepth; j++) o->quality[o->nq++] = backupQ.q[j];
            o->n_best = tDepth;
            for (int j = 0; j < tDepth; j++) { o->best_rows[j][0] = backupQ.rows[j][0]; o->best_rows[j][1] = backupQ.rows[j][1]; }
        }
    }
    return nopt;
}

/* ===== makeList_Half ===== */
int make_list_half(int n, int now_n, const perm_t *sbox, int slen,
                   const cons_t *cons, const int *nlist, int nlen, int depth, mlopt_t *out) {
    /* sbox 는 슬라이스하지 않음(full). sbox.index 파리티용 inv. */
    for (int i = 0; i < slen; i++) inv_a[sbox[i]] = i;
    /* 순차 사전패스: normal(짝수) 위치 행만 통과 → 통과 후보 인덱스를 순서대로 수집.
     * 병렬 영역에서 out[k] 슬롯을 원본과 동일 순서로 채우기 위함. */
    int nopt = 0;
    for (int i = 0; i + 1 < nlen; i += 2)
        if ((inv_a[nlist[i]] & 1) == 0) half_idx[nopt++] = i;
    #pragma omp parallel for schedule(dynamic)
    for (int k = 0; k < nopt; k++) {
        int i = half_idx[k];
        int nownow_n = now_n;
        mlopt_t *o = &out[k];
        o->rows[0] = nlist[i]; o->rows[1] = nlist[i+1]; o->nq = 0; o->free_count = 0;
        memcpy(ml_sbox, sbox, (size_t)slen * sizeof(perm_t));
        ml_cons = *cons;
        memcpy(ml_nlist, nlist, (size_t)nlen * sizeof(int));
        int wlen = nlen, costs[2];
        int rows[2] = { nlist[i], nlist[i+1] };
        block_t res;
        make_block(n, nownow_n, ml_sbox, &ml_cons, ml_nlist, &wlen, rows, &res);
        costs[0] = res.costGB; costs[1] = res.costAL;
        if (ml_cons.count >= 1 && is_reduce(ml_cons.s[0], nownow_n) && nownow_n > 2) {
            ml_cons.count = 0; nownow_n--;        /* half 는 sbox 슬라이스 안 함 */
        }
        o->quality[o->nq++] = costs[0] + costs[1];
        int ne, no;
        fb_list(nownow_n, ml_nlist, wlen, ml_sbox, slen, fb_even, &ne, fb_odd, &no);
        o->free_count = ne >> 1;                  /* even free block 만 */
        if (depth == 0) continue;
        /* tempEvenList: tempSbox.index(tempNList[i])&1 == (i&1) 인 것 */
        for (int j = 0; j < slen; j++) inv_b[ml_sbox[j]] = j;
        int te = 0;
        for (int j = 0; j < wlen; j++)
            if ((inv_b[ml_nlist[j]] & 1) == (j & 1)) temp_even[te++] = ml_nlist[j];
        int tDepth = depth; if (depth > (te >> 1)) tDepth = te >> 1;
        int nowQ[MAX_QUALITY], bestQ[MAX_QUALITY];
        for (int j = 0; j < tDepth; j++) { nowQ[j] = 100; bestQ[j] = 100; }
        depth_exhaustive(n, nownow_n, ml_sbox, slen, &ml_cons, temp_even, te, nowQ, bestQ, 0, tDepth);
        for (int j = 0; j < tDepth; j++) o->quality[o->nq++] = bestQ[j];
    }
    return nopt;
}
