/*
 * Copyright (c) 2008-2010 Stefan Krah. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
 * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 * OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 * OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 * SUCH DAMAGE.
 */


#include "mpdecimal.h"
#include <stdio.h>
#include <assert.h>
#include "numbertheory.h"
#include "umodarith.h"
#include "crt.h"


/*
 * Functions for arithmetic on triple-word mpd_uint_t numbers.
 */


/* Multiply P1P2 by v, store result in w. */
static inline void
_crt_mulP1P2_3(mpd_uint_t w[3], mpd_uint_t v)
{
	mpd_uint_t hi1, hi2, lo;

	_mpd_mul_words(&hi1, &lo, LH_P1P2, v);
	w[0] = lo;

	_mpd_mul_words(&hi2, &lo, UH_P1P2, v);
	lo = hi1 + lo;
	if (lo < hi1) hi2++;

	w[1] = lo;
	w[2] = hi2;
}

/* Add 3 words from v to w. The result is known to fit in w. */
static inline void
_crt_add3(mpd_uint_t w[3], mpd_uint_t v[3])
{
	mpd_uint_t carry;

	w[0] = w[0] + v[0];
	carry = (w[0] < v[0]);

	w[1] = w[1] + v[1];
	if (w[1] < v[1]) w[2]++;

	w[1] = w[1] + carry;
	if (w[1] < carry) w[2]++;

	w[2] += v[2];
}

/* Divide 3 words in u by v, store result in w, return remainder. */
static inline mpd_uint_t
_crt_div3(mpd_uint_t *w, const mpd_uint_t *u, mpd_uint_t v)
{
	mpd_uint_t r1 = u[2];
	mpd_uint_t r2;

	if (r1 < v) {
		w[2] = 0;
	}
	else {
		_mpd_div_word(&w[2], &r1, u[2], v); /* GCOV_NOT_REACHED */
	}

	_mpd_div_words(&w[1], &r2, r1, u[1], v);
	_mpd_div_words(&w[0], &r1, r2, u[0], v);

	return r1;
}


/*
 * Chinese Remainder Theorem:
 * Algorithm from Joerg Arndt, "Matters Computational",
 * Chapter 37.4.1 [http://www.jjj.de/fxt/]
 */

/*
 * CRT with carry: x1, x2, x3 contain numbers modulo p1, p2, p3. For each
 * triple of members of the arrays, find the unique z modulo p1*p2*p3.
 *
 * Overflow analysis for 32 bit:
 *
 * carry[3] can hold cmax = 2**96-1. Let c_i denote the carry at the
 * beginning of the ith iteration. Let zmax be the maximum z.
 *
 * cmax = 2**96-1      = 79228162514264337593543950335
 * zmax = (p1*p2*p3)-1 = 7711435583600944683209981953
 *
 * c_0 = 0
 * c_1 = (c_0 + zmax) / 10**9 = 7711435583600944683
 * c_2 = (c_1 + zmax) / 10**9 = 7711435591312380266
 * c_3 = (c_2 + zmax) / 10**9 = 7711435591312380274
 * c_4 = (c_3 + zmax) / 10**9 = 7711435591312380274
 * (...)
 *
 * The carries do not increase, (c_i + zmax) cannot overflow.
 *
 *
 * Overflow analysis for 64 bit:
 *
 * cmax = 2**192-1     = 6277101735386680763835789423207666416102355444464034512895
 * zmax = (p1*p2*p3)-1 = 6277101353934753858413533876806988331203900781075588186113
 *
 * c_0 = 0
 * c_1 = (c_0 + zmax) / 10**19 = 627710135393475385841353387680698833120
 * c_2 = (c_1 + zmax) / 10**19 = 627710135393475385904124401220046371704
 * c_3 = (c_2 + zmax) / 10**19 = 627710135393475385904124401220046371710
 * c_4 = (c_3 + zmax) / 10**19 = 627710135393475385904124401220046371710
 * (...)
 *
 * The carries do not increase. (c_i + zmax) cannot overflow.
 */
void
crt3(mpd_uint_t *x1, mpd_uint_t *x2, mpd_uint_t *x3, mpd_size_t rsize)
{
	mpd_uint_t p1 = mpd_moduli[P1];
	mpd_uint_t umod;
#ifdef PPRO
	double dmod;
	uint32_t dinvmod[3];
#endif
	mpd_uint_t a1, a2, a3;
	mpd_uint_t s;
	mpd_uint_t z[3], t[3];
	mpd_uint_t carry[3] = {0,0,0};
	mpd_uint_t hi, lo;
	mpd_size_t i;

	for (i = 0; i < rsize; i++) {

		a1 = x1[i];
		a2 = x2[i];
		a3 = x3[i];

		SETMODULUS(P2);
		s = ext_submod(a2, a1, umod);
		s = MULMOD(s, INV_P1_MOD_P2);

		_mpd_mul_words(&hi, &lo, s, p1);
		lo = lo + a1;
		if (lo < a1) hi++;

		SETMODULUS(P3);
		s = dw_submod(a3, hi, lo, umod);
		s = MULMOD(s, INV_P1P2_MOD_P3);

		z[0] = lo;
		z[1] = hi;
		z[2] = 0;

		_crt_mulP1P2_3(t, s);
		_crt_add3(z, t);
	 	_crt_add3(carry, z);

		x1[i] = _crt_div3(carry, carry, MPD_RADIX);
	}

	assert(carry[0] == 0 && carry[1] == 0 && carry[2] == 0);
}


