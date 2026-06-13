#include "block_ops.h"
#include <string.h>

static int s_to_int(const char *s, int len) { int v = 0; for (int i = 0; i < len; i++) v = (v << 1) | (s[i] - '0'); return v; }

static int pybin3(unsigned v, char *out) {
    if (v == 0) { out[0] = '\0'; return 0; }
    int msb = 31; while (((v >> msb) & 1u) == 0) msb--;
    int k = 0;
    for (int b = msb - 1; b >= 0; b--) out[k++] = (char)('0' + ((v >> b) & 1u));
    out[k] = '\0';
    return k;
}

/* ===== sub_CONS ===== */
int sub_cons(int n, int index1, int index2, const cons_t *cons, gate_t *out) {
    int m = 0;
    char nextPos[MAXN + 1];
    next_position(n, cons, nextPos);
    int rightPos = s_to_int(nextPos, n - 1);

    char ssd[40];
    int ssd_len = pybin3((unsigned)(((1u << n) + (unsigned)index1) ^ (unsigned)index2), ssd);  /* strStartDiff (swap 전, XOR 대칭) */

    if (index2 < index1) { int t = index1; index1 = index2; index2 = t; }

    int head_len = ssd_len - 1; if (head_len < 0) head_len = 0;   /* ssd[:-1] */
    int startHead1 = 0; for (int i = 0; i < head_len; i++) if (ssd[i] == '1') startHead1++;
    if (startHead1 == 0) return 0;                                 /* already block */

    char buf[40];
    /* step 1. parity 교정 */
    if (ssd_len > 0 && ssd[ssd_len - 1] == '0') {
        int intCon = 0; for (int i = 0; i < head_len; i++) if (ssd[i] == '1') { intCon = i + 1; break; }
        int intTar = n;
        char b2[40]; int b2l = pybin3((unsigned)((1u << n) + (unsigned)index2), b2);
        char b1[40]; pybin3((unsigned)((1u << n) + (unsigned)index1), b1);
        int bitval;
        if ((b2l > 0 ? b2[b2l - 1] : '0') == '0') bitval = b2[intCon - 1] - '0';
        else                                       bitval = b1[intCon - 1] - '0';
        gate_init(&out[m], n - intTar); gate_add_ctrl(&out[m], n - intCon, bitval); m++;
        index1 = gate_to_index(n, &out[m-1], index1);
        index2 = gate_to_index(n, &out[m-1], index2);
    }

    /* step 2. 마지막 비트 포함 2비트만 다르게 */
    int l = pybin3((unsigned)(((1u << n) + (unsigned)index1) ^ (unsigned)index2), buf);
    int nd = l - 1; if (nd < 0) nd = 0;                            /* [3:-1] */
    int intCon = 0; for (int i = 0; i < nd; i++) if (buf[i] == '1') { intCon = i + 1; break; }

    if (nextPos[intCon - 1] == '1') {                             /* step 2-1 */
        gate_init(&out[m], n - intCon); m++;
        index1 = gate_to_index(n, &out[m-1], index1);
        index2 = gate_to_index(n, &out[m-1], index2);
    }
    for (int rep = 0; rep < startHead1 - 1; rep++) {              /* step 2-2 */
        l = pybin3((unsigned)(((1u << n) + (unsigned)index1) ^ (unsigned)index2), buf);
        nd = l - 1; if (nd < 0) nd = 0;
        int intTar = 0; for (int i = intCon; i < nd; i++) if (buf[i] == '1') { intTar = i + 1; break; }  /* .index('1', intCon) */
        gate_init(&out[m], n - intTar); gate_add_ctrl(&out[m], n - intCon, 1); m++;
        index1 = gate_to_index(n, &out[m-1], index1);
        index2 = gate_to_index(n, &out[m-1], index2);
    }
    if (nextPos[intCon - 1] == '1') {                             /* step 2-3 */
        gate_init(&out[m], n - intCon); m++;
        index1 = gate_to_index(n, &out[m-1], index1);
        index2 = gate_to_index(n, &out[m-1], index2);
    }

    /* step 3. C^m X */
    l = pybin3((unsigned)(((1u << n) + (unsigned)index1) ^ (unsigned)index2), buf);
    nd = l - 1; if (nd < 0) nd = 0;
    int cnt1 = 0; for (int i = 0; i < nd; i++) if (buf[i] == '1') cnt1++;
    if (cons->count == 0 && cnt1 == 1) {
        int intTar = 0; for (int i = 0; i < nd; i++) if (buf[i] == '1') { intTar = i + 1; break; }
        gate_init(&out[m], n - intTar); gate_add_ctrl(&out[m], n - n, 1); m++;
    } else {
        int intTar = 0; for (int i = 0; i < nd; i++) if (buf[i] == '1') { intTar = i + 1; break; }
        char chk[42];
        int cl = pybin3((unsigned)(((1u << (n - 1)) + (unsigned)rightPos) ^ (unsigned)(index1 >> 1)), chk);
        chk[cl] = '1'; chk[cl + 1] = '\0';                        /* + '1' */
        int end = 0; for (int i = 0; chk[i]; i++) if (chk[i] == '1') { end = i + 1; break; }
        gate_init(&out[m], n - intTar);
        int nConsList = 0;
        for (int i = 0; i < end; i++) if (nextPos[i] == '1') { gate_add_ctrl(&out[m], n - (i + 1), 1); nConsList++; }
        int npc = 0; for (int i = 0; nextPos[i]; i++) if (nextPos[i] == '1') npc++;
        if (npc > nConsList) gate_add_ctrl(&out[m], n - end, (index1 >> (n - end)) & 1);
        gate_add_ctrl(&out[m], n - n, index2 & 1);
        m++;
    }
    return m;
}

/* ===== sub_ALLOC ===== */
int sub_alloc(int n, int index1, int index2, const cons_t *cons, gate_t *out) {
    (void)index2;
    int m = 0;
    char nextPos[MAXN + 1];
    next_position(n, cons, nextPos);
    int rightPos = s_to_int(nextPos, n - 1);

    char ssd[40];
    int ssd_len = pybin3((unsigned)(((1u << (n - 1)) + (unsigned)rightPos) ^ (unsigned)(index1 >> 1)), ssd);
    int start1 = 0; for (int i = 0; i < ssd_len; i++) if (ssd[i] == '1') start1++;

    if (n == 2 && start1 == 1) { gate_init(&out[m], n - 1); m++; return m; }

    char buf[40];
    for (int rep = 0; rep < start1 - 1; rep++) {                  /* step 1 */
        int l = pybin3((unsigned)(((1u << (n - 1)) + (unsigned)rightPos) ^ (unsigned)(index1 >> 1)), buf);
        int intCon = 0; for (int i = 0; i < l; i++) if (buf[i] == '1') { intCon = i + 1; break; }
        int intTar = 0; for (int i = intCon; i < l; i++) if (buf[i] == '1') { intTar = i + 1; break; }
        int val = 1, found = 0;
        for (int c = 0; c < cons->count; c++) {
            if (cons->s[c][intCon - 1] != '-' && cons->s[c][intTar - 1] != '-') {
                val = (cons->s[c][intCon - 1] - '0') ^ 1; found = 1; break;
            }
        }
        if (!found) val = 1;
        gate_init(&out[m], n - intTar); gate_add_ctrl(&out[m], n - intCon, val); m++;
        index1 = gate_to_index(n, &out[m-1], index1);
    }

    int l = pybin3((unsigned)(((1u << (n - 1)) + (unsigned)rightPos) ^ (unsigned)(index1 >> 1)), buf);  /* step 2 */
    int cnt1 = 0; for (int i = 0; i < l; i++) if (buf[i] == '1') cnt1++;
    if (cnt1 == 1) {
        int intTar = 0; for (int i = 0; i < l; i++) if (buf[i] == '1') { intTar = i + 1; break; }
        gate_init(&out[m], n - intTar);
        for (int i = 0; i < n - intTar; i++)                      /* nextPos[intTar:] */
            if (nextPos[intTar + i] == '1') gate_add_ctrl(&out[m], n - (intTar + i + 1), 1);
        m++;
    }
    return m;
}

/* ===== common helper ===== */
static int find_val(const perm_t *a, int len, perm_t v) {
    for (int i = 0; i < len; i++) if (a[i] == v) return i;
    return -1;
}
static int gcost(const gate_t *g) { return (g->n_ctrl > 1) ? (2 * g->n_ctrl - 3) : 0; }

static int nr2_tmp[MAX_PERM];
#pragma omp threadprivate(nr2_tmp)
static void nlist_remove2(int *nlist, int *nlen, int ir) {
    int len = *nlen;
    int keep = 0;
    for (int i = 0; i < ir && i < len; i++) nr2_tmp[keep++] = nlist[i];
    for (int i = ir + 2; i < len; i++) nr2_tmp[keep++] = nlist[i];
    for (int i = 0; i < keep; i++) nlist[i] = nr2_tmp[i];
    *nlen = keep;
}
static void cons_advance(int now_n, cons_t *cons) {   /* cons_update(now_n, cons+[next_position]) */
    char np[MAXN + 1];
    next_position(now_n, cons, np);
    cons_push(cons, np);
    cons_update(now_n, cons);
}

/* ===== makeBlock ===== */
void make_block(int n, int now_n, perm_t *sbox, cons_t *cons,
                int *nlist, int *nlen, const int now_rows[2], block_t *res) {
    int tlen = 1 << now_n;
    perm_t *tail = sbox + ((1 << n) - tlen);

    /* construct */
    int idx0 = find_val(tail, tlen, (perm_t)now_rows[0]);
    int idx1 = find_val(tail, tlen, (perm_t)now_rows[1]);
    int gc = sub_cons(now_n, idx0, idx1, cons, res->construct);
    if (now_n != n && gc > 0)
        for (int j = 0; j < n - now_n; j++)
            gate_add_ctrl(&res->construct[gc - 1], n - 1 - j, 1);
    res->n_construct = gc;
    int costGB = 0;
    for (int j = 0; j < gc; j++) { apply_gate(n, sbox, &res->construct[j]); costGB += gcost(&res->construct[j]); }

    /* allocate (tail 변경 후 위치 재조회) */
    idx0 = find_val(tail, tlen, (perm_t)now_rows[0]);
    idx1 = find_val(tail, tlen, (perm_t)now_rows[1]);
    int ga = sub_alloc(now_n, idx0, idx1, cons, res->allocate);
    res->n_allocate = ga;
    int costAL = 0;
    for (int j = 0; j < ga; j++) { apply_gate(n, sbox, &res->allocate[j]); costAL += gcost(&res->allocate[j]); }

    int irx = -1; for (int i = 0; i < *nlen; i++) if (nlist[i] == now_rows[0]) { irx = i; break; }
    nlist_remove2(nlist, nlen, irx);
    cons_advance(now_n, cons);
    res->costGB = costGB; res->costAL = costAL;
}

/* ===== makeBlock_Reduction ===== */
void make_block_reduction(int n, int now_n, perm_t *sbox, cons_t *cons,
                          int *nlist, int *nlen, const int now_rows[2], block_t *res) {
    int tlen = 1 << now_n;
    perm_t *tail = sbox + ((1 << n) - tlen);

    int idx0 = find_val(tail, tlen, (perm_t)now_rows[0]);
    int idx1 = find_val(tail, tlen, (perm_t)now_rows[1]);
    int gc = sub_cons(now_n, idx0, idx1, cons, res->construct);
    for (int j = 0; j < gc; j++) apply_gate(now_n, tail, &res->construct[j]);   /* 적용 먼저 */
    if (now_n != n && gc > 0)                                                   /* 그 다음 보정 */
        for (int j = 0; j < n - now_n; j++)
            gate_add_ctrl(&res->construct[gc - 1], n - 1 - j, 1);
    res->n_construct = gc;
    int costGB = 0;
    for (int j = 0; j < gc; j++) costGB += gcost(&res->construct[j]);

    idx0 = find_val(tail, tlen, (perm_t)now_rows[0]);
    idx1 = find_val(tail, tlen, (perm_t)now_rows[1]);
    int ga = sub_alloc(now_n, idx0, idx1, cons, res->allocate);
    res->n_allocate = ga;
    int costAL = 0;
    for (int j = 0; j < ga; j++) { apply_gate(now_n, tail, &res->allocate[j]); costAL += gcost(&res->allocate[j]); }

    int irx = -1; for (int i = 0; i < *nlen; i++) if (nlist[i] == now_rows[0]) { irx = i; break; }
    nlist_remove2(nlist, nlen, irx);
    cons_advance(now_n, cons);
    res->costGB = costGB; res->costAL = costAL;
}

/* ===== makeBlock_semi ===== (length of sbox is 2^now_n) */
void make_block_semi(int n, int now_n, perm_t *sbox, int slen, cons_t *cons,
                     int *nlist, int *nlen, const int now_rows[2], int costs[2]) {
    gate_t g[SUB_MAX_GATES];

    int idx0 = find_val(sbox, slen, (perm_t)now_rows[0]);
    int idx1 = find_val(sbox, slen, (perm_t)now_rows[1]);
    int gc = sub_cons(now_n, idx0, idx1, cons, g);
    int costGB = 0;
    if (now_n != n && gc > 0) {
        for (int j = 0; j < gc - 1; j++) { apply_gate(now_n, sbox, &g[j]); costGB += gcost(&g[j]); }
        apply_gate(now_n, sbox, &g[gc - 1]);
        costGB += 2 * (g[gc - 1].n_ctrl + n - now_n) - 3;     /* 마지막 게이트 cost 보정 */
    } else {
        for (int j = 0; j < gc; j++) { apply_gate(now_n, sbox, &g[j]); costGB += gcost(&g[j]); }
    }

    idx0 = find_val(sbox, slen, (perm_t)now_rows[0]);
    idx1 = find_val(sbox, slen, (perm_t)now_rows[1]);
    int ga = sub_alloc(now_n, idx0, idx1, cons, g);
    int costAL = 0;
    for (int j = 0; j < ga; j++) { apply_gate(now_n, sbox, &g[j]); costAL += gcost(&g[j]); }

    int irx = -1; for (int i = 0; i < *nlen; i++) if (nlist[i] == now_rows[0]) { irx = i; break; }
    nlist_remove2(nlist, nlen, irx);
    cons_advance(now_n, cons);
    costs[0] = costGB; costs[1] = costAL;
}
