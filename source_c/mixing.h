/*   alg_mixing       (alg_mixing)        : n<=12 용 탐욕+제한 depth mixing
 *   alg_mixing_more  (alg_mixingMore)    : Toffoli 동원 확장 탐색 (fallback)
 *   new_mixing       (newMixing)         : n>12 용 생성기 product 기반 mixing
 *   alg_preprocessing(alg_preprocessing) : 전처리 전체 파이프라인
 */
#ifndef MIXING_H
#define MIXING_H

#include "leaf_utils.h"
#include "block_ops.h"

#define MIX_MAX_GATES  (1 << 16)

int alg_mixing(int n, const perm_t *sbox, gate_t *out);
int alg_mixing_more(int n, const perm_t *sbox, gate_t *out);
int new_mixing(int n, const perm_t *sbox, gate_t *out);
int alg_preprocessing(int n, const perm_t *sbox, gate_t *out);

#endif /* MIXING_H */
