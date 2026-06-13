#include "reduction.h"
#include <string.h>

#define MAX_OPT (1 << 16)   /* nopt = nlen/2 <= 2^(n-1) <= 2^15 (n<=16) */

static int      rd_nlist[MAX_PERM];
static perm_t   rd_pwork[MAX_PERM];
static int      rd_inv[MAX_PERM];
static mlopt_t  rd_opt[MAX_OPT];
static mlopt2_t rd_opt2[MAX_OPT];

/* ---- rbuf 헬퍼 ---- */
static void rb_group(rbuf_t *rb, const gate_t *g, int cnt) {
    int off = rb->gpool_n;
    for (int i = 0; i < cnt; i++) rb->gpool[off + i] = g[i];
    rb->gpool_n += cnt;
    rb->grp[rb->n_grp].off = off;
    rb->grp[rb->n_grp].len = cnt;
    rb->n_grp++;
}
/* 마지막 그룹에 게이트 1개 추가 (nthPrime hardcoded 용). 마지막 그룹이 풀의 끝이라고 가정. */
static void rb_append_last(rbuf_t *rb, const gate_t *g) {
    rb->gpool[rb->gpool_n++] = *g;
    rb->grp[rb->n_grp - 1].len += 1;
}

static int ml2_sum(const mlopt2_t *o) { int s = 0; for (int i = 0; i < o->nq; i++) s += o->quality[i]; return s; }
static void ml2_stable_sort(mlopt2_t *a, int k) {
    for (int i = 1; i < k; i++) {
        mlopt2_t x = a[i]; int kx = ml2_sum(&x); int j = i - 1;
        while (j >= 0 && ml2_sum(&a[j]) > kx) { a[j+1] = a[j]; j--; }
        a[j+1] = x;
    }
}

/* ===== alg_reduction_for_Left ===== */
void alg_reduction_for_left(int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb, perm_t *out) {
    int L = 1 << n;
    perm_t *tS = out;
    memcpy(tS, sbox, (size_t)L * sizeof(perm_t));
    int nlen = L; for (int i = 0; i < L; i++) rd_nlist[i] = i;
    cons_t cons; cons_clear(&cons);

    for (int now_n = n; now_n > 1; now_n--) {
        int numMade = 0;
        double limit = (now_n >= 3) ? (double)(1 << (now_n - 3)) : 0.5;
        while ((double)numMade < limit) {
            int npd = parDepth[n - now_n];
            int rows[2] = { -1, -1 };
            if (npd != 0) {
                npd -= 1;
                int m = make_list_half(n, n, tS, L, &cons, rd_nlist, nlen, npd, rd_opt);
                choose(rd_opt, m, rows);
            } else {
                perm_build_inv(tS, L, rd_inv);
                for (int i = 0; i + 1 < nlen; i += 2)
                    if ((rd_inv[rd_nlist[i]] & 1) == 0) { rows[0] = rd_nlist[i]; rows[1] = rd_nlist[i+1]; break; }
            }
            block_t res;
            make_block(n, n, tS, &cons, rd_nlist, &nlen, rows, &res);
            rb_group(rb, res.construct, res.n_construct);
            rb_group(rb, res.allocate,  res.n_allocate);
            numMade++;
        }
    }
}

/* ===== alg_reduction_prime ===== */
void alg_reduction_prime(int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb) {
    int L = 1 << n;
    perm_t *tS = rd_pwork;
    memcpy(tS, sbox, (size_t)L * sizeof(perm_t));
    int nlen = L;
    for (int i = 0; i < L; i++) rd_nlist[i] = (int)sbox[i];
    /* nList = sorted(sbox) */
    for (int a = 1; a < nlen; a++) { int v = rd_nlist[a], j = a - 1; while (j >= 0 && rd_nlist[j] > v) { rd_nlist[j+1] = rd_nlist[j]; j--; } rd_nlist[j+1] = v; }

    int now_n = n;
    while (now_n > 1) {
        cons_t cons; cons_clear(&cons);
        int numMade = 0;
        block_t res;

        if (now_n == 4) {
            int oddFlag = parity_of_sbox(n, tS);
            int m = make_list2_full(n, now_n, tS, L, &cons, rd_nlist, nlen, oddFlag, 3, rd_opt2);
            ml2_stable_sort(rd_opt2, m);
            mlopt2_t *b = &rd_opt2[0];
            make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, b->rows, &res);
            rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
            for (int j = 0; j < b->n_best; j++) {
                int r[2] = { b->best_rows[j][0], b->best_rows[j][1] };
                make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, r, &res);
                rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
            }
            now_n -= 1; continue;
        }

        while (numMade < (1 << (now_n - 2))) {
            int npd = parDepth[n - now_n];
            int rows[2];
            if (npd != 0) {
                npd -= 1;
                int m = make_list_full(n, now_n, tS, L, &cons, rd_nlist, nlen, npd, rd_opt);
                choose(rd_opt, m, rows);
            } else {
                rows[0] = rd_nlist[0]; rows[1] = rd_nlist[1];
            }
            make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, rows, &res);
            rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
            numMade++;
            if (now_n == 5 && numMade == 7) break;
        }

        if (now_n == 5 && numMade == 7) {
            int oddFlag = parity_of_sbox(n, tS);
            int m = make_list2_full(n, now_n, tS, L, &cons, rd_nlist, nlen, oddFlag, 4, rd_opt2);
            ml2_stable_sort(rd_opt2, m);
            mlopt2_t *b = &rd_opt2[0];
            make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, b->rows, &res);
            rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
            cons_clear(&cons); now_n -= 1; numMade = 0;
            for (int j = 0; j < b->n_best; j++) {
                int r[2] = { b->best_rows[j][0], b->best_rows[j][1] };
                make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, r, &res);
                rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
                numMade++;
            }
            now_n -= 1; continue;
        }
        now_n -= 1;
    }
}

/* ===== alg_reduction ===== */
/* prime 그룹들의 게이트 중 제어비트 0 을 포함하면 [n-1,1] 제어 추가 */
static void adjust_prime(rbuf_t *rb, int from_grp, int n) {
    for (int gi = from_grp; gi < rb->n_grp; gi++) {
        rgroup_t *G = &rb->grp[gi];
        for (int k = 0; k < G->len; k++) {
            gate_t *g = &rb->gpool[G->off + k];
            int has0 = 0; for (int c = 0; c < g->n_ctrl; c++) if (g->ctrl_bit[c] == 0) { has0 = 1; break; }
            if (has0) gate_add_ctrl(g, n - 1, 1);
        }
    }
}

void alg_reduction(int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb) {
    static perm_t tS[MAX_PERM];
    alg_reduction_for_left(n, sbox, parDepth, rb, tS);
    int prime_start = rb->n_grp;
    alg_reduction_prime(n - 1, tS + (1 << (n - 1)), parDepth, rb);
    adjust_prime(rb, prime_start, n);
    rb->has_last = 1;
    gate_init(&rb->last, n - n); gate_add_ctrl(&rb->last, n - 1, 1);
}

/* ===== nthPrime 변형 ===== */
/* hardcoded gate 추가 헬퍼: target=n-n, 제어 목록 (bit,val) */
static void hc_gate(gate_t *g, int n, const int (*cv)[2], int ncv) {
    gate_init(g, n - n);
    for (int i = 0; i < ncv; i++) gate_add_ctrl(g, cv[i][0], cv[i][1]);
}

void alg_reduction_for_left_nthprime(int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb, perm_t *out) {
    int L = 1 << n;
    perm_t *tS = out;
    memcpy(tS, sbox, (size_t)L * sizeof(perm_t));
    int nlen = L; for (int i = 0; i < L; i++) rd_nlist[i] = i;
    cons_t cons; cons_clear(&cons);
    int tNumBlock = 0;

    for (int now_n = n; now_n > 1; now_n--) {
        int numMade = 0;
        double limit = (now_n >= 3) ? (double)(1 << (now_n - 3)) : 0.5;
        while ((double)numMade < limit) {
            int npd = parDepth[n - now_n];
            int rows[2] = { -1, -1 };
            if (npd != 0) {
                npd -= 1;
                int m = make_list_half(n, n, tS, L, &cons, rd_nlist, nlen, npd, rd_opt);
                choose(rd_opt, m, rows);
            } else {
                int found = 0;
                for (int i = tNumBlock * 2; i + 1 < L; i += 2)
                    if ((int)tS[i+1] - (int)tS[i] == 1 && (tS[i] & 1) == 0) { rows[0] = tS[i]; rows[1] = tS[i+1]; found = 1; break; }
                if (!found) {
                    perm_build_inv(tS, L, rd_inv);
                    for (int i = 0; i + 1 < nlen; i += 2)
                        if ((rd_inv[rd_nlist[i]] & 1) == 0) { rows[0] = rd_nlist[i]; rows[1] = rd_nlist[i+1]; break; }
                }
            }
            block_t res;
            make_block(n, n, tS, &cons, rd_nlist, &nlen, rows, &res);
            rb_group(rb, res.construct, res.n_construct);
            rb_group(rb, res.allocate,  res.n_allocate);
            numMade++; tNumBlock++;

            /* nthPrime hardcoded 보정 (특정 n/시점) */
            if (n == 13 && now_n == 8 && numMade == 30) {
                const int g1[][2] = {{n-1,1}}; const int g2[][2] = {{n-1,0},{n-2,1},{n-3,1},{n-4,1},{n-5,1},{n-6,1},{n-7,1}};
                const int g3[][2] = {{n-1,0},{n-2,1},{n-3,1},{n-4,1},{n-5,1},{n-6,1},{n-7,0},{n-8,1},{n-9,1},{n-10,1},{n-11,1}};
                gate_t g; hc_gate(&g,n,g1,1); rb_append_last(rb,&g); apply_gate(n,tS,&g);
                hc_gate(&g,n,g2,7); rb_append_last(rb,&g); apply_gate(n,tS,&g);
                hc_gate(&g,n,g3,11); rb_append_last(rb,&g); apply_gate(n,tS,&g);
            } else if (n == 14 && now_n == 9 && numMade == 48) {
                const int g1[][2] = {{n-1,1}}; const int g2[][2] = {{n-1,0},{n-2,1},{n-3,1},{n-4,1},{n-5,1},{n-6,1},{n-7,1}};
                const int g3[][2] = {{n-1,0},{n-2,1},{n-3,1},{n-4,1},{n-5,1},{n-6,1},{n-7,0},{n-8,1},{n-9,1}};
                gate_t g; hc_gate(&g,n,g1,1); rb_append_last(rb,&g); apply_gate(n,tS,&g);
                hc_gate(&g,n,g2,7); rb_append_last(rb,&g); apply_gate(n,tS,&g);
                hc_gate(&g,n,g3,9); rb_append_last(rb,&g); apply_gate(n,tS,&g);
            } else if (n == 15 && now_n == 9 && numMade == 45) {
                const int g1[][2] = {{n-1,1}};
                const int g2[][2] = {{n-1,0},{n-2,1},{n-3,1},{n-4,1},{n-5,1},{n-6,1},{n-7,1},{n-8,1}};
                const int g3[][2] = {{n-1,0},{n-2,1},{n-3,1},{n-4,1},{n-5,1},{n-6,1},{n-7,1},{n-8,0},{n-9,1},{n-10,1}};
                const int g4[][2] = {{n-1,0},{n-2,1},{n-3,1},{n-4,1},{n-5,1},{n-6,1},{n-7,1},{n-8,0},{n-9,1},{n-10,0},{n-11,1},{n-12,1}};
                const int g5[][2] = {{n-1,0},{n-2,1},{n-3,1},{n-4,1},{n-5,1},{n-6,1},{n-7,1},{n-8,0},{n-9,1},{n-10,0},{n-11,1},{n-12,1},{n-13,0},{n-14,0}};
                gate_t g; hc_gate(&g,n,g1,1); rb_append_last(rb,&g); apply_gate(n,tS,&g);
                hc_gate(&g,n,g2,8); rb_append_last(rb,&g); apply_gate(n,tS,&g);
                hc_gate(&g,n,g3,10); rb_append_last(rb,&g); apply_gate(n,tS,&g);
                hc_gate(&g,n,g4,12); rb_append_last(rb,&g); apply_gate(n,tS,&g);
                hc_gate(&g,n,g5,14); rb_append_last(rb,&g); apply_gate(n,tS,&g);
            }
        }
    }
}

void alg_reduction_prime_nthprime(int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb) {
    int L = 1 << n;
    perm_t *tS = rd_pwork;
    memcpy(tS, sbox, (size_t)L * sizeof(perm_t));
    int nlen = L; for (int i = 0; i < L; i++) rd_nlist[i] = (int)sbox[i];
    for (int a = 1; a < nlen; a++) { int v = rd_nlist[a], j = a - 1; while (j >= 0 && rd_nlist[j] > v) { rd_nlist[j+1] = rd_nlist[j]; j--; } rd_nlist[j+1] = v; }
    int tNumBlock = 0;

    int now_n = n;
    while (now_n > 1) {
        cons_t cons; cons_clear(&cons);
        int numMade = 0; block_t res;

        if (now_n == 4) {
            int oddFlag = parity_of_sbox(n, tS);
            int m = make_list2_full(n, now_n, tS, L, &cons, rd_nlist, nlen, oddFlag, 3, rd_opt2);
            ml2_stable_sort(rd_opt2, m);
            mlopt2_t *b = &rd_opt2[0];
            make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, b->rows, &res);
            rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
            for (int j = 0; j < b->n_best; j++) {
                int r[2] = { b->best_rows[j][0], b->best_rows[j][1] };
                make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, r, &res);
                rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
            }
            now_n -= 1; continue;
        }

        while (numMade < (1 << (now_n - 2))) {
            int npd = parDepth[n - now_n];
            int rows[2];
            if (npd != 0) {
                npd -= 1;
                int m = make_list_full(n, now_n, tS, L, &cons, rd_nlist, nlen, npd, rd_opt);
                choose(rd_opt, m, rows);
            } else {
                int special = (n == 7 && now_n == n && numMade < 7) || (n == 9 && now_n == n && numMade < 14)
                           || (n == 11 && now_n == n && numMade < 3) || (n == 15 && now_n == n && numMade < 154);
                if (special) {
                    int found = 0;
                    for (int i = tNumBlock * 2; i + 1 < L; i += 2)
                        if ((int)tS[i+1] - (int)tS[i] == 1 && (tS[i] & 1) == 0) { rows[0] = tS[i]; rows[1] = tS[i+1]; found = 1; break; }
                    if (!found) {
                        perm_build_inv(tS, L, rd_inv);
                        for (int i = 0; i + 1 < nlen; i += 2)
                            if ((rd_inv[rd_nlist[i]] & 1) == 0) { rows[0] = rd_nlist[i]; rows[1] = rd_nlist[i+1]; break; }
                    }
                } else { rows[0] = rd_nlist[0]; rows[1] = rd_nlist[1]; }
            }
            make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, rows, &res);
            rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
            numMade++; tNumBlock++;

            if (n == 7 && now_n == n && numMade == 7) {
                const int a1[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0}};
                const int a2[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0},{n-4,1},{n-5,1},{n-6,1}};
                gate_t g; hc_gate(&g,n,a1,4); rb_append_last(rb,&g); hc_gate(&g,n,a2,7); rb_append_last(rb,&g);
            } else if (n == 9 && now_n == n && numMade == 14) {
                const int a1[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0},{n-4,0}};
                const int a2[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0},{n-4,0},{n-5,1},{n-6,1},{n-7,1}};
                gate_t g; hc_gate(&g,n,a1,5); rb_append_last(rb,&g); hc_gate(&g,n,a2,8); rb_append_last(rb,&g);
            } else if (n == 11 && now_n == n && numMade == 3) {
                const int a1[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0},{n-4,0},{n-5,0},{n-6,0},{n-7,0},{n-8,0}};
                const int a2[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0},{n-4,0},{n-5,0},{n-6,0},{n-7,0},{n-8,0},{n-9,1},{n-10,1}};
                gate_t g; hc_gate(&g,n,a1,9); rb_append_last(rb,&g); hc_gate(&g,n,a2,11); rb_append_last(rb,&g);
            } else if (n == 15 && now_n == n && numMade == 156) {
                const int a1[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0},{n-4,0},{n-5,0},{n-6,0},{n-7,0},{n-8,0}};
                const int a2[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0},{n-4,0},{n-5,0},{n-6,0},{n-7,0},{n-8,1},{n-9,0},{n-10,0},{n-11,0}};
                const int a3[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0},{n-4,0},{n-5,0},{n-6,0},{n-7,0},{n-8,1},{n-9,0},{n-10,0},{n-11,1},{n-12,0}};
                const int a4[][2] = {{n,1},{n-1,0},{n-2,0},{n-3,0},{n-4,0},{n-5,0},{n-6,0},{n-7,0},{n-8,1},{n-9,0},{n-10,0},{n-11,1},{n-12,1},{n-13,0},{n-14,0}};
                gate_t g; hc_gate(&g,n,a1,9); rb_append_last(rb,&g); hc_gate(&g,n,a2,12); rb_append_last(rb,&g);
                hc_gate(&g,n,a3,13); rb_append_last(rb,&g); hc_gate(&g,n,a4,15); rb_append_last(rb,&g);
            }

            if (now_n == 5 && numMade == 7) break;
        }

        if (now_n == 5 && numMade == 7) {
            int oddFlag = parity_of_sbox(n, tS);
            int m = make_list2_full(n, now_n, tS, L, &cons, rd_nlist, nlen, oddFlag, 4, rd_opt2);
            ml2_stable_sort(rd_opt2, m);
            mlopt2_t *b = &rd_opt2[0];
            make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, b->rows, &res);
            rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
            cons_clear(&cons); now_n -= 1; numMade = 0;
            for (int j = 0; j < b->n_best; j++) {
                int r[2] = { b->best_rows[j][0], b->best_rows[j][1] };
                make_block_reduction(n, now_n, tS, &cons, rd_nlist, &nlen, r, &res);
                rb_group(rb, res.construct, res.n_construct); rb_group(rb, res.allocate, res.n_allocate);
                numMade++;
            }
            now_n -= 1; continue;
        }
        now_n -= 1;
    }
}

void alg_reduction_nthprime(int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb) {
    static perm_t tS[MAX_PERM];
    alg_reduction_for_left_nthprime(n, sbox, parDepth, rb, tS);
    int prime_start = rb->n_grp;
    alg_reduction_prime_nthprime(n - 1, tS + (1 << (n - 1)), parDepth, rb);
    adjust_prime(rb, prime_start, n);
    /* LastGate */
    if (n == 8 || n == 9 || n == 10 || n == 11 || n == 12 || n == 16) {
        rb->has_last = 1; gate_init(&rb->last, n - n); gate_add_ctrl(&rb->last, n - 1, 1);
    } else {
        rb->has_last = 1; gate_set_null(&rb->last);   /* [[]] : 빈(널) 게이트 */
    }
}
