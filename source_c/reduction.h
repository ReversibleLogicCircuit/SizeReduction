/*   alg_reduction            (alg_reduction)            : for_Left + prime + CX1n
 *   alg_reduction_for_left   (alg_reduction_for_Left)   : 좌측 절반 블록 구성
 *   alg_reduction_prime      (alg_reduction_prime)      : 우측 블록 분해
 *   alg_reduction_nthprime / _for_left_nthprime / _prime_nthprime : nthPrime 벤치 변형
 */
#ifndef REDUCTION_H
#define REDUCTION_H

#include "exhaustive.h"   /* make_list_*, mlopt_t, mlopt2_t, block_ops, leaf_utils, unit_opers */

typedef struct { int off, len; } rgroup_t;

typedef struct {
    gate_t   *gpool;  int gpool_cap, gpool_n;   /* 게이트 풀 (caller 제공) */
    rgroup_t *grp;    int grp_cap,  n_grp;      /* 그룹 목록 (caller 제공) */
    int has_last; gate_t last;                  /* alg_reduction 의 마지막 단일 게이트 */
} rbuf_t;

static inline void rbuf_reset(rbuf_t *rb) { rb->gpool_n = 0; rb->n_grp = 0; rb->has_last = 0; }

/* parDepth: 길이 >= n 의 정수 배열 (now_n 별 exhaustive depth). */
void alg_reduction_for_left(int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb, perm_t *out_tSbox);
void alg_reduction_prime  (int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb);
void alg_reduction        (int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb);

void alg_reduction_for_left_nthprime(int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb, perm_t *out_tSbox);
void alg_reduction_prime_nthprime   (int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb);
void alg_reduction_nthprime         (int n, const perm_t *sbox, const int *parDepth, rbuf_t *rb);

#endif /* REDUCTION_H */
