// var Cip = function () {
//     function O(e, t, r, n) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         n = n | 0;
//         b(0x0000, 0x0800, 0x1000, T, e, t, r, n)
//     }
//     function I(e, t, r, n) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         n = n | 0;
//         var o = 0;
//         b(0x0400, 0x0c00, 0x2000, T, e, n, r, t);
//         o = i,
//         i = a,
//         a = o
//     }
//     function R(e, t, r, l) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         l = l | 0;
//         b(0x0000, 0x0800, 0x1000, T, s ^ e, u ^ t, f ^ r, c ^ l);
//         s = n,
//         u = i,
//         f = o,
//         c = a
//     }
//     function N(e, t, r, l) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         l = l | 0;
//         var d = 0;
//         b(0x0400, 0x0c00, 0x2000, T, e, l, r, t);
//         d = i,
//         i = a,
//         a = d;
//         n = n ^ s,
//         i = i ^ u,
//         o = o ^ f,
//         a = a ^ c;
//         s = e,
//         u = t,
//         f = r,
//         c = l
//     }
//     function D(e, t, r, l) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         l = l | 0;
//         b(0x0000, 0x0800, 0x1000, T, s, u, f, c);
//         s = n = n ^ e,
//         u = i = i ^ t,
//         f = o = o ^ r,
//         c = a = a ^ l
//     }
//     function x(e, t, r, l) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         l = l | 0;
//         b(0x0000, 0x0800, 0x1000, T, s, u, f, c);
//         n = n ^ e,
//         i = i ^ t,
//         o = o ^ r,
//         a = a ^ l;
//         s = e,
//         u = t,
//         f = r,
//         c = l
//     }
//     function L(e, t, r, l) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         l = l | 0;
//         b(0x0000, 0x0800, 0x1000, T, s, u, f, c);
//         s = n,
//         u = i,
//         f = o,
//         c = a;
//         n = n ^ e,
//         i = i ^ t,
//         o = o ^ r,
//         a = a ^ l
//     }
//     function M(e, t, r, s) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         s = s | 0;
//         b(0x0000, 0x0800, 0x1000, T, l, d, h, _);
//         _ = ~y & _ | y & _ + 1;
//         h = ~g & h | g & h + ((_ | 0) == 0);
//         d = ~E & d | E & d + ((h | 0) == 0);
//         l = ~p & l | p & l + ((d | 0) == 0);
//         n = n ^ e;
//         i = i ^ t;
//         o = o ^ r;
//         a = a ^ s
//     }
//     function P(e, t, r, n) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         n = n | 0;
//         var i = 0
//           , o = 0
//           , a = 0
//           , l = 0
//           , d = 0
//           , h = 0
//           , _ = 0
//           , p = 0
//           , E = 0
//           , g = 0;
//         e = e ^ s,
//         t = t ^ u,
//         r = r ^ f,
//         n = n ^ c;
//         i = m | 0,
//         o = v | 0,
//         a = S | 0,
//         l = A | 0;
//         for (; (E | 0) < 128; E = E + 1 | 0) {
//             if (i >>> 31) {
//                 d = d ^ e,
//                 h = h ^ t,
//                 _ = _ ^ r,
//                 p = p ^ n
//             }
//             i = i << 1 | o >>> 31,
//             o = o << 1 | a >>> 31,
//             a = a << 1 | l >>> 31,
//             l = l << 1;
//             g = n & 1;
//             n = n >>> 1 | r << 31,
//             r = r >>> 1 | t << 31,
//             t = t >>> 1 | e << 31,
//             e = e >>> 1;
//             if (g)
//                 e = e ^ 0xe1000000
//         }
//         s = d,
//         u = h,
//         f = _,
//         c = p
//     }
//     function U(e) {
//         e = e | 0;
//         T = e
//     }
//     function B(e, t, r, s) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         s = s | 0;
//         n = e,
//         i = t,
//         o = r,
//         a = s
//     }
//     function k(e, t, r, n) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         n = n | 0;
//         s = e,
//         u = t,
//         f = r,
//         c = n
//     }
//     function G(e, t, r, n) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         n = n | 0;
//         l = e,
//         d = t,
//         h = r,
//         _ = n
//     }
//     function q(e, t, r, n) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         n = n | 0;
//         p = e,
//         E = t,
//         g = r,
//         y = n
//     }
//     function F(e, t, r, n) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         n = n | 0;
//         _ = ~y & _ | y & n,
//         h = ~g & h | g & r,
//         d = ~E & d | E & t,
//         l = ~p & l | p & e
//     }
//     function W(e) {
//         e = e | 0;
//         if (e & 15)
//             return -1;
//         w[e | 0] = n >>> 24,
//         w[e | 1] = n >>> 16 & 255,
//         w[e | 2] = n >>> 8 & 255,
//         w[e | 3] = n & 255,
//         w[e | 4] = i >>> 24,
//         w[e | 5] = i >>> 16 & 255,
//         w[e | 6] = i >>> 8 & 255,
//         w[e | 7] = i & 255,
//         w[e | 8] = o >>> 24,
//         w[e | 9] = o >>> 16 & 255,
//         w[e | 10] = o >>> 8 & 255,
//         w[e | 11] = o & 255,
//         w[e | 12] = a >>> 24,
//         w[e | 13] = a >>> 16 & 255,
//         w[e | 14] = a >>> 8 & 255,
//         w[e | 15] = a & 255;
//         return 16
//     }
//     function j(e) {
//         e = e | 0;
//         if (e & 15)
//             return -1;
//         w[e | 0] = s >>> 24,
//         w[e | 1] = s >>> 16 & 255,
//         w[e | 2] = s >>> 8 & 255,
//         w[e | 3] = s & 255,
//         w[e | 4] = u >>> 24,
//         w[e | 5] = u >>> 16 & 255,
//         w[e | 6] = u >>> 8 & 255,
//         w[e | 7] = u & 255,
//         w[e | 8] = f >>> 24,
//         w[e | 9] = f >>> 16 & 255,
//         w[e | 10] = f >>> 8 & 255,
//         w[e | 11] = f & 255,
//         w[e | 12] = c >>> 24,
//         w[e | 13] = c >>> 16 & 255,
//         w[e | 14] = c >>> 8 & 255,
//         w[e | 15] = c & 255;
//         return 16
//     }
//     function K() {
//         O(0, 0, 0, 0);
//         m = n,
//         v = i,
//         S = o,
//         A = a
//     }
//     function H(e, t, r) {
//         e = e | 0;
//         t = t | 0;
//         r = r | 0;
//         var s = 0;
//         if (t & 15)
//             return -1;
//         while ((r | 0) >= 16) {
//             V[e & 7](w[t | 0] << 24 | w[t | 1] << 16 | w[t | 2] << 8 | w[t | 3], w[t | 4] << 24 | w[t | 5] << 16 | w[t | 6] << 8 | w[t | 7], w[t | 8] << 24 | w[t | 9] << 16 | w[t | 10] << 8 | w[t | 11], w[t | 12] << 24 | w[t | 13] << 16 | w[t | 14] << 8 | w[t | 15]);
//             w[t | 0] = n >>> 24,
//             w[t | 1] = n >>> 16 & 255,
//             w[t | 2] = n >>> 8 & 255,
//             w[t | 3] = n & 255,
//             w[t | 4] = i >>> 24,
//             w[t | 5] = i >>> 16 & 255,
//             w[t | 6] = i >>> 8 & 255,
//             w[t | 7] = i & 255,
//             w[t | 8] = o >>> 24,
//             w[t | 9] = o >>> 16 & 255,
//             w[t | 10] = o >>> 8 & 255,
//             w[t | 11] = o & 255,
//             w[t | 12] = a >>> 24,
//             w[t | 13] = a >>> 16 & 255,
//             w[t | 14] = a >>> 8 & 255,
//             w[t | 15] = a & 255;
//             s = s + 16 | 0,
//             t = t + 16 | 0,
//             r = r - 16 | 0
//         }
//         return s | 0
//     }
// }

//
// data = String.fromCharCode( 65, 66, 67, 68, 69, 70, 71 )
// console.log(data);

var b = new Buffer('zhangsan');
var s = b.toString('base64');
console.log(s);
// SmF2YVNjcmlwdA==