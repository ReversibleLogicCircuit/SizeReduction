#ifndef EXHAUSTIVE_H
#define EXHAUSTIVE_H

#include "leaf_utils.h"   /* mlopt_t, fb_list */
#include "block_ops.h"    /* make_block, make_block_semi */

typedef struct {
    int rows[2];
    int quality[MAX_QUALITY]; int nq;
    int free_count;
    int best_rows[MAX_QUALITY][2]; int n_best;
} mlopt2_t;

int make_list_full (int n, int now_n, const perm_t *sbox, int slen,
                    const cons_t *cons, const int *nlist, int nlen, int depth, mlopt_t *out);
int make_list_half (int n, int now_n, const perm_t *sbox, int slen,
                    const cons_t *cons, const int *nlist, int nlen, int depth, mlopt_t *out);
int make_list2_full(int n, int now_n, const perm_t *sbox, int slen,
                    const cons_t *cons, const int *nlist, int nlen, int oddflag, int depth, mlopt2_t *out);

#endif /* EXHAUSTIVE_H */
