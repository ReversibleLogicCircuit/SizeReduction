#ifndef LEAF_UTILS_H
#define LEAF_UTILS_H

#include "unit_opers.h"

/* 게이트 생성기 출력 버퍼 권장 크기 (n<=16 에서 tof_gates 최대 6720 < 8192). */
#define LEAF_MAX_GEN   8192

/* choose 용 옵션의 quality 배열 최대 길이 */
#define MAX_QUALITY    32

/* write_gate / write_tfc_gate 한 줄 최대 길이, 최대 줄 수 */
#define GATE_STR_MAX   96
#define GATE_MAX_LINES 64

/* ---- 게이트 생성기 (out 에 기록, 반환=개수). out 크기 >= LEAF_MAX_GEN 권장 ---- */
int cn_gates(int n, gate_t *out);              /* CNGates */
int cn_last_target_gates(int n, gate_t *out);  /* CN_LastTargetGates */
int tof_gates(int n, gate_t *out);             /* TofGates */
int tof_last_target_gates(int n, gate_t *out); /* Tof_LastTargetGates */

void fb_list(int n, const int *number_list, int nlen,
             const perm_t *sbox, int slen,
             perm_t *even, int *neven, perm_t *odd, int *nodd);

typedef struct {
    int rows[2];
    int quality[MAX_QUALITY];
    int nq;
    int free_count;
} mlopt_t;

void choose(mlopt_t *opts, int n_opt, int out_rows[2]);

int write_gate(int n, const gate_t *g, char out[][GATE_STR_MAX], int maxlines);
int write_tfc_gate(int n, const gate_t *g, char out[][GATE_STR_MAX], int maxlines);

#endif /* LEAF_UTILS_H */
