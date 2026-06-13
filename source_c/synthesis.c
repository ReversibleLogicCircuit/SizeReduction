#include "synthesis.h"
#include <stdio.h>
#include <string.h>

static perm_t syn_tS[MAX_PERM];
static perm_t syn_tmp[MAX_PERM];
static gate_t syn_pp[MIX_MAX_GATES];
static gate_t syn_rgpool[1 << 21];   /* 라운드별 reduction 게이트(최대 ~0.5M@16비트), 여유 2.1M */
static rgroup_t syn_rgrp[1 << 18];   /* 라운드별 그룹(최대 ~65k@16비트), 여유 262k */

/* 게이트 좌표를 full-n 으로 보정 (target / 제어비트 += n_diff) */
static void adj(gate_t *g, int nd) {
    if (gate_is_null(g)) return;
    g->target += nd;
    for (int k = 0; k < g->n_ctrl; k++) g->ctrl_bit[k] += nd;
}

/* ===== alg_serach (2비트) ===== */
int alg_serach(const perm_t *sbox, gate_t *out) {
    int no = 0;
    perm_t tS[4]; for (int i = 0; i < 4; i++) tS[i] = sbox[i];
    cons_t cons; cons_clear(&cons);
    int nlist[4] = {0,1,2,3}, nlen = 4, rows[2] = {0,1};
    block_t res;
    make_block(2, 2, tS, &cons, nlist, &nlen, rows, &res);
    for (int k = 0; k < res.n_construct; k++) out[no++] = res.construct[k];
    for (int k = 0; k < res.n_allocate;  k++) out[no++] = res.allocate[k];

    option_t opt[2]; int m = return_options(2, tS, opt);
    int c1 = 0; for (int i = 0; i < m; i++) if (opt[i].parity == 1) c1++;
    if (c1 == 1) {
        gate_t g; gate_init(&g, 0); gate_add_ctrl(&g, 1, (tS[0] == 0) ? 1 : 0);
        apply_gate(2, tS, &g); out[no++] = g;
    } else if (c1 == 2) {
        gate_t g; gate_init(&g, 0);     /* X gate */
        apply_gate(2, tS, &g); out[no++] = g;
    }
    return no;
}

/* ===== alg_synthesis ===== */
int alg_synthesis(int n, const perm_t *sbox, const int *depths, gate_t *out) {
    int no = 0;
    memcpy(syn_tS, sbox, (size_t)(1 << n) * sizeof(perm_t));
    rbuf_t rb; rb.gpool = syn_rgpool; rb.gpool_cap = 1 << 21; rb.grp = syn_rgrp; rb.grp_cap = 1 << 18;

    for (int now_n = n; now_n > 2; now_n--) {
        int nd = n - now_n;

        /* preprocessing : 적용(now_n) 후 보정해서 저장 */
        int npp = alg_preprocessing(now_n, syn_tS, syn_pp);
        for (int k = 0; k < npp; k++) {
            apply_gate(now_n, syn_tS, &syn_pp[k]);
            gate_t g = syn_pp[k]; adj(&g, nd); out[no++] = g;
        }

        /* reduction : steps[:-1] = 모든 그룹 적용(now_n) 후 보정 저장, 마지막 단일 게이트는 보정만 */
        rbuf_reset(&rb);
        alg_reduction(now_n, syn_tS, depths + (n - now_n), &rb);
        for (int gi = 0; gi < rb.n_grp; gi++) {
            rgroup_t *G = &rb.grp[gi];
            for (int k = 0; k < G->len; k++) {
                gate_t *gg = &rb.gpool[G->off + k];
                apply_gate(now_n, syn_tS, gg);
                gate_t g = *gg; adj(&g, nd); out[no++] = g;
            }
        }
        { gate_t g = rb.last; adj(&g, nd); out[no++] = g; }   /* CX1n (적용 안 함) */

        /* 비트 축소: tempSbox[i] = tSbox[2i] // 2 */
        int half = 1 << (now_n - 1);
        for (int i = 0; i < half; i++) syn_tmp[i] = syn_tS[2 * i] >> 1;
        memcpy(syn_tS, syn_tmp, (size_t)half * sizeof(perm_t));
    }

    /* 2비트 search */
    gate_t e2[64]; int ne2 = alg_serach(syn_tS, e2);
    for (int k = 0; k < ne2; k++) {
        apply_gate(2, syn_tS, &e2[k]);
        gate_t g = e2[k]; adj(&g, n - 2); out[no++] = g;
    }
    return no;
}

/* ===== apply_circuit (검증용) ===== */
void apply_circuit(int n, perm_t *sbox, const gate_t *gates, int ngates) {
    for (int i = 0; i < ngates; i++) apply_gate(n, sbox, &gates[i]);
}

/* ===== write_real_format ===== */
void write_real_format(int n, const gate_t *gates, int ngates, const char *path) {
    FILE *fp = fopen(path, "w");
    if (!fp) return;
    fprintf(fp, ".version 2.0\n.numvars %d\n", n);
    fprintf(fp, ".variables"); for (int i = 0; i < n; i++) fprintf(fp, " x%d", i + 1); fprintf(fp, "\n");
    fprintf(fp, ".inputs");    for (int i = 0; i < n; i++) fprintf(fp, " i%d", i + 1); fprintf(fp, "\n");
    fprintf(fp, ".outputs");   for (int i = 0; i < n; i++) fprintf(fp, " o%d", i + 1); fprintf(fp, "\n");
    fprintf(fp, ".constants "); for (int i = 0; i < n; i++) fputc('-', fp); fprintf(fp, "\n");
    fprintf(fp, ".garbage ");   for (int i = 0; i < n; i++) fputc('-', fp); fprintf(fp, "\n");
    fprintf(fp, ".begin\n");
    char lines[GATE_MAX_LINES][GATE_STR_MAX];
    for (int i = 0; i < ngates; i++) {
        int m = write_gate(n, &gates[i], lines, GATE_MAX_LINES);
        for (int j = 0; j < m; j++) fprintf(fp, "%s\n", lines[j]);
    }
    fprintf(fp, ".end");
    fclose(fp);
}
