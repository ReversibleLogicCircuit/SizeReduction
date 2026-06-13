/*   alg_synthesis   (alg_synthesis)     : 전체 합성. preprocessing+reduction 반복 + 2비트 search
 *   alg_serach      (alg_serach)        : 2비트 치환 합성
 *   write_real_format (writeRealFormat) : REAL 포맷 파일 출력
 *   apply_circuit   (apply_Qube_gates)  : 회로를 치환에 적용(검증용)
 */
#ifndef SYNTHESIS_H
#define SYNTHESIS_H

#include "reduction.h"
#include "mixing.h"

#define SYN_MAX_GATES (1 << 21)   /* 회로 게이트 상한. n=16 총 게이트 ~1M, 여유 2.1M */

/* 2비트 합성: out 에 게이트 기록, 개수 반환 (2비트 좌표). */
int alg_serach(const perm_t *sbox, gate_t *out);

/* 전체 합성: out 에 회로(full-n 좌표, emission 순서) 기록, 게이트 개수 반환.
 * depths: 길이 >= n 정수 배열(now_n 별 exhaustive depth). out >= SYN_MAX_GATES 권장. */
int alg_synthesis(int n, const perm_t *sbox, const int *depths, gate_t *out);

/* 회로를 sbox 에 순서대로 적용 (full n). 검증: 결과가 항등이면 회로가 입력 치환을 구현. */
void apply_circuit(int n, perm_t *sbox, const gate_t *gates, int ngates);

/* REAL 포맷 파일 출력. */
void write_real_format(int n, const gate_t *gates, int ngates, const char *path);

#endif /* SYNTHESIS_H */
