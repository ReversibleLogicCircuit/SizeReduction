#ifndef BLOCK_OPS_H
#define BLOCK_OPS_H

#include "unit_opers.h"

#define SUB_MAX_GATES  64

int sub_cons(int n, int index1, int index2, const cons_t *cons, gate_t *out);
int sub_alloc(int n, int index1, int index2, const cons_t *cons, gate_t *out);

typedef struct {
    gate_t construct[SUB_MAX_GATES]; int n_construct;
    gate_t allocate[SUB_MAX_GATES];  int n_allocate;
    int costGB, costAL;
} block_t;

void make_block(int n, int now_n, perm_t *sbox, cons_t *cons,
                int *nlist, int *nlen, const int now_rows[2], block_t *res);

void make_block_reduction(int n, int now_n, perm_t *sbox, cons_t *cons,
                          int *nlist, int *nlen, const int now_rows[2], block_t *res);

void make_block_semi(int n, int now_n, perm_t *sbox, int slen, cons_t *cons,
                     int *nlist, int *nlen, const int now_rows[2], int costs[2]);

#endif /* BLOCK_OPS_H */
