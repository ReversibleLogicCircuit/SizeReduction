#include "leaf_utils.h"
#include <stdio.h>
#include <string.h>

int cn_gates(int n, gate_t *out) {
    int m = 0;
    for (int a = 0; a < n; a++)
        for (int b = a + 1; b < n; b++) {
            gate_init(&out[m], a); gate_add_ctrl(&out[m], b, 1); m++;
            gate_init(&out[m], a); gate_add_ctrl(&out[m], b, 0); m++;
            gate_init(&out[m], b); gate_add_ctrl(&out[m], a, 1); m++;
            gate_init(&out[m], b); gate_add_ctrl(&out[m], a, 0); m++;
        }
    return m;
}

int cn_last_target_gates(int n, gate_t *out) {
    int m = 0;
    for (int c = 1; c < n; c++) {
        gate_init(&out[m], 0); gate_add_ctrl(&out[m], c, 1); m++;
        gate_init(&out[m], 0); gate_add_ctrl(&out[m], c, 0); m++;
    }
    return m;
}

int tof_gates(int n, gate_t *out) {
    int m = 0;
    for (int a = 0; a < n; a++)
    for (int b = a + 1; b < n; b++)
    for (int c = b + 1; c < n; c++) {
        /* target a */
        gate_init(&out[m],a); gate_add_ctrl(&out[m],b,1); gate_add_ctrl(&out[m],c,1); m++;
        gate_init(&out[m],a); gate_add_ctrl(&out[m],b,0); gate_add_ctrl(&out[m],c,1); m++;
        gate_init(&out[m],a); gate_add_ctrl(&out[m],b,1); gate_add_ctrl(&out[m],c,0); m++;
        gate_init(&out[m],a); gate_add_ctrl(&out[m],b,0); gate_add_ctrl(&out[m],c,0); m++;
        /* target b */
        gate_init(&out[m],b); gate_add_ctrl(&out[m],c,1); gate_add_ctrl(&out[m],a,1); m++;
        gate_init(&out[m],b); gate_add_ctrl(&out[m],c,0); gate_add_ctrl(&out[m],a,1); m++;
        gate_init(&out[m],b); gate_add_ctrl(&out[m],c,1); gate_add_ctrl(&out[m],a,0); m++;
        gate_init(&out[m],b); gate_add_ctrl(&out[m],c,0); gate_add_ctrl(&out[m],a,0); m++;
        /* target c */
        gate_init(&out[m],c); gate_add_ctrl(&out[m],b,1); gate_add_ctrl(&out[m],a,1); m++;
        gate_init(&out[m],c); gate_add_ctrl(&out[m],b,0); gate_add_ctrl(&out[m],a,1); m++;
        gate_init(&out[m],c); gate_add_ctrl(&out[m],b,1); gate_add_ctrl(&out[m],a,0); m++;
        gate_init(&out[m],c); gate_add_ctrl(&out[m],b,0); gate_add_ctrl(&out[m],a,0); m++;
    }
    return m;
}

int tof_last_target_gates(int n, gate_t *out) {
    int m = 0;
    for (int a = 1; a < n; a++)
    for (int b = a + 1; b < n; b++) {
        gate_init(&out[m],0); gate_add_ctrl(&out[m],a,1); gate_add_ctrl(&out[m],b,1); m++;
        gate_init(&out[m],0); gate_add_ctrl(&out[m],a,0); gate_add_ctrl(&out[m],b,1); m++;
        gate_init(&out[m],0); gate_add_ctrl(&out[m],a,1); gate_add_ctrl(&out[m],b,0); m++;
        gate_init(&out[m],0); gate_add_ctrl(&out[m],a,0); gate_add_ctrl(&out[m],b,0); m++;
    }
    return m;
}

/* ===== FBList ===== */
static int fb_inv[MAX_PERM];
#pragma omp threadprivate(fb_inv)
void fb_list(int n, const int *number_list, int nlen,
             const perm_t *sbox, int slen,
             perm_t *even, int *neven, perm_t *odd, int *nodd) {
    int *inv = fb_inv;
    for (int i = 0; i < slen; i++) inv[sbox[i]] = i;
    int ne = 0, no = 0;
    const int top = n - 1;  /* 상위 (n-1) 비트 비교: 위치가 LSB만 다르면 동일 */
    for (int i = 0; i < nlen / 2; i++) {
        int n1 = inv[number_list[2*i + 0]];
        int n2 = inv[number_list[2*i + 1]];
        if ((n1 >> 1) == (n2 >> 1) && top >= 1) {  /* 상위 n-1비트 동일 == n1>>1==n2>>1 */
            if ((n1 & 1) == 0) { even[ne++] = sbox[n1]; even[ne++] = sbox[n2]; }
            else               { odd[no++]  = sbox[n1]; odd[no++]  = sbox[n2]; }
        }
    }
    *neven = ne; *nodd = no;
}

/* ===== choose ===== */
static long key_free(const mlopt_t *o, int c) { (void)c; return -(long)o->free_count; }
static long key_q(const mlopt_t *o, int c)    { return o->quality[c]; }
static long key_sum(const mlopt_t *o, int c)  { (void)c; long s = 0; for (int i = 0; i < o->nq; i++) s += o->quality[i]; return s; }

/* 안정(stable) 삽입정렬: key 오름차순. (Python sorted 의 안정성 재현) */
static void stable_sort(mlopt_t *a, int k, long (*key)(const mlopt_t*, int), int ctx) {
    for (int i = 1; i < k; i++) {
        mlopt_t x = a[i];
        long kx = key(&x, ctx);
        int j = i - 1;
        while (j >= 0 && key(&a[j], ctx) > kx) { a[j+1] = a[j]; j--; }
        a[j+1] = x;
    }
}

void choose(mlopt_t *opts, int n_opt, int out_rows[2]) {
    if (n_opt <= 0) return;
    stable_sort(opts, n_opt, key_free, 0);            /* free_count 내림차순(key=-free) */
    int nq = opts[0].nq;
    for (int di = nq; di >= 1; di--)
        stable_sort(opts, n_opt, key_q, di - 1);      /* quality[di-1] 오름차순 */
    stable_sort(opts, n_opt, key_sum, 0);             /* sum(quality) 오름차순 */
    out_rows[0] = opts[0].rows[0];
    out_rows[1] = opts[0].rows[1];
}

/* ===== writeGate / writeTFCGate ===== */
static int write_gate_impl(int n, const gate_t *g, char out[][GATE_STR_MAX],
                           int maxlines, char sep) {
    if (gate_is_null(g)) return 0;
    if (g->n_ctrl == 0) {
        snprintf(out[0], GATE_STR_MAX, "t1 x%d", n - g->target);
        return 1;
    }
    /* 제어값 0 인 비트의 X 게이트 줄 (gate[1] 순서대로) */
    char xlines[MAX_CTRL][GATE_STR_MAX];
    int nx = 0;
    for (int k = 0; k < g->n_ctrl; k++)
        if (g->ctrl_val[k] == 0)
            snprintf(xlines[nx++], GATE_STR_MAX, "t1 x%d", n - g->ctrl_bit[k]);

    /* 본체 게이트 줄 */
    char body[GATE_STR_MAX];
    int p = snprintf(body, GATE_STR_MAX, "t%d ", g->n_ctrl + 1);
    for (int k = 0; k < g->n_ctrl; k++)
        p += snprintf(body + p, GATE_STR_MAX - p, "x%d%c", n - g->ctrl_bit[k], sep);
    snprintf(body + p, GATE_STR_MAX - p, "x%d", n - g->target);

    /* result = xlines + [body] + xlines */
    int m = 0;
    for (int i = 0; i < nx && m < maxlines; i++) strcpy(out[m++], xlines[i]);
    if (m < maxlines) strcpy(out[m++], body);
    for (int i = 0; i < nx && m < maxlines; i++) strcpy(out[m++], xlines[i]);
    return m;
}

int write_gate(int n, const gate_t *g, char out[][GATE_STR_MAX], int maxlines) {
    return write_gate_impl(n, g, out, maxlines, ' ');   /* REAL: 공백 구분 */
}
int write_tfc_gate(int n, const gate_t *g, char out[][GATE_STR_MAX], int maxlines) {
    return write_gate_impl(n, g, out, maxlines, ',');   /* TFC: 콤마 구분 */
}
