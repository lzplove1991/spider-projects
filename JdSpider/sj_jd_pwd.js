//q: btoa js代码
var q = {};
    q.PADCHAR = "=",
    q.ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
    q.getbyte = function(t, e) {
        var i = t.charCodeAt(e);
        if (i > 255)
            throw "INVALID_CHARACTER_ERR: DOM Exception 5";
        return i
    }
    ,
    q.encode = function(t) {
        if (1 != arguments.length)
            throw "SyntaxError: Not enough arguments";
        var e, i, n = q.PADCHAR, o = q.ALPHA, p = q.getbyte, r = [];
        t = "" + t;
        var s = t.length - t.length % 3;
        if (0 == t.length)
            return t;
        for (e = 0; e < s; e += 3)
            i = p(t, e) << 16 | p(t, e + 1) << 8 | p(t, e + 2),
            r.push(o.charAt(i >> 18)),
            r.push(o.charAt(i >> 12 & 63)),
            r.push(o.charAt(i >> 6 & 63)),
            r.push(o.charAt(63 & i));
        switch (t.length - s) {
        case 1:
            i = p(t, e) << 16,
            r.push(o.charAt(i >> 18) + o.charAt(i >> 12 & 63) + n + n);
            break;
        case 2:
            i = p(t, e) << 16 | p(t, e + 1) << 8,
            r.push(o.charAt(i >> 18) + o.charAt(i >> 12 & 63) + o.charAt(i >> 6 & 63) + n)
        }
        return r.join("")
    }
// 以下密码和用户名加密的js代码
var window ={};
function CtoH(obj) {
    var pos = obj.selectionEnd;
    var str = obj.value;
    var result = "";
    for (var i = 0; i < str.length; i++) {
        if (str.charCodeAt(i) == 12288) {
            result += String.fromCharCode(str.charCodeAt(i) - 12256);
            continue
        }
        if (str.charCodeAt(i) > 65280 && str.charCodeAt(i) < 65375) {
            result += String.fromCharCode(str.charCodeAt(i) - 65248)
        } else {
            result += String.fromCharCode(str.charCodeAt(i))
        }
    }
    obj.value = result;
    obj.setSelectionRange(pos, pos);
    return result
}
function BarrettMu(i) {
    this.modulus = biCopy(i),
    this.k = biHighIndex(this.modulus) + 1;
    var t = new BigInt;
    t.digits[2 * this.k] = 1,
    this.mu = biDivide(t, this.modulus),
    this.bkplus1 = new BigInt,
    this.bkplus1.digits[this.k + 1] = 1,
    this.modulo = BarrettMu_modulo,
    this.multiplyMod = BarrettMu_multiplyMod,
    this.powMod = BarrettMu_powMod
}
function BarrettMu_modulo(i) {
    var t = biDivideByRadixPower(i, this.k - 1)
      , r = biMultiply(t, this.mu)
      , e = biDivideByRadixPower(r, this.k + 1)
      , n = biModuloByRadixPower(i, this.k + 1)
      , g = biMultiply(e, this.modulus)
      , s = biModuloByRadixPower(g, this.k + 1)
      , d = biSubtract(n, s);
    d.isNeg && (d = biAdd(d, this.bkplus1));
    for (var o = biCompare(d, this.modulus) >= 0; o; )
        d = biSubtract(d, this.modulus),
        o = biCompare(d, this.modulus) >= 0;
    return d
}
function BarrettMu_multiplyMod(i, t) {
    var r = biMultiply(i, t);
    return this.modulo(r)
}
function BarrettMu_powMod(i, t) {
    var r = new BigInt;
    r.digits[0] = 1;
    for (var e = i, n = t; ; ) {
        if (0 != (1 & n.digits[0]) && (r = this.multiplyMod(r, e)),
        n = biShiftRight(n, 1),
        0 == n.digits[0] && 0 == biHighIndex(n))
            break;
        e = this.multiplyMod(e, e)
    }
    return r
}
function setMaxDigits(i) {
    maxDigits = i,
    ZERO_ARRAY = new Array(maxDigits);
    for (var t = 0; t < ZERO_ARRAY.length; t++)
        ZERO_ARRAY[t] = 0;
    bigZero = new BigInt,
    bigOne = new BigInt,
    bigOne.digits[0] = 1
}
function BigInt(i) {
    "boolean" == typeof i && 1 == i ? this.digits = null : this.digits = ZERO_ARRAY.slice(0),
    this.isNeg = !1
}
function biFromDecimal(i) {
    for (var t, r = "-" == i.charAt(0), e = r ? 1 : 0; e < i.length && "0" == i.charAt(e); )
        ++e;
    if (e == i.length)
        t = new BigInt;
    else {
        var n = i.length - e
          , g = n % dpl10;
        for (0 == g && (g = dpl10),
        t = biFromNumber(Number(i.substr(e, g))),
        e += g; e < i.length; )
            t = biAdd(biMultiply(t, lr10), biFromNumber(Number(i.substr(e, dpl10)))),
            e += dpl10;
        t.isNeg = r
    }
    return t
}
function biCopy(i) {
    var t = new BigInt((!0));
    return t.digits = i.digits.slice(0),
    t.isNeg = i.isNeg,
    t
}
function biFromNumber(i) {
    var t = new BigInt;
    t.isNeg = i < 0,
    i = Math.abs(i);
    for (var r = 0; i > 0; )
        t.digits[r++] = i & maxDigitVal,
        i >>= biRadixBits;
    return t
}
function reverseStr(i) {
    for (var t = "", r = i.length - 1; r > -1; --r)
        t += i.charAt(r);
    return t
}
function biToString(i, t) {
    var r = new BigInt;
    r.digits[0] = t;
    for (var e = biDivideModulo(i, r), n = hexatrigesimalToChar[e[1].digits[0]]; 1 == biCompare(e[0], bigZero); )
        e = biDivideModulo(e[0], r),
        digit = e[1].digits[0],
        n += hexatrigesimalToChar[e[1].digits[0]];
    return (i.isNeg ? "-" : "") + reverseStr(n)
}
function biToDecimal(i) {
    var t = new BigInt;
    t.digits[0] = 10;
    for (var r = biDivideModulo(i, t), e = String(r[1].digits[0]); 1 == biCompare(r[0], bigZero); )
        r = biDivideModulo(r[0], t),
        e += String(r[1].digits[0]);
    return (i.isNeg ? "-" : "") + reverseStr(e)
}
function digitToHex(t) {
    var r = 15
      , e = "";
    for (i = 0; i < 4; ++i)
        e += hexToChar[t & r],
        t >>>= 4;
    return reverseStr(e)
}
function biToHex(i) {
    for (var t = "", r = (biHighIndex(i),
    biHighIndex(i)); r > -1; --r)
        t += digitToHex(i.digits[r]);
    return t
}
function charToHex(i) {
    var t, r = 48, e = r + 9, n = 97, g = n + 25, s = 65, d = 90;
    return t = i >= r && i <= e ? i - r : i >= s && i <= d ? 10 + i - s : i >= n && i <= g ? 10 + i - n : 0
}
function hexToDigit(i) {
    for (var t = 0, r = Math.min(i.length, 4), e = 0; e < r; ++e)
        t <<= 4,
        t |= charToHex(i.charCodeAt(e));
    return t
}
function biFromHex(i) {
    for (var t = new BigInt, r = i.length, e = r, n = 0; e > 0; e -= 4,
    ++n)
        t.digits[n] = hexToDigit(i.substr(Math.max(e - 4, 0), Math.min(e, 4)));
    return t
}
function biFromString(i, t) {
    var r = "-" == i.charAt(0)
      , e = r ? 1 : 0
      , n = new BigInt
      , g = new BigInt;
    g.digits[0] = 1;
    for (var s = i.length - 1; s >= e; s--) {
        var d = i.charCodeAt(s)
          , o = charToHex(d)
          , a = biMultiplyDigit(g, o);
        n = biAdd(n, a),
        g = biMultiplyDigit(g, t)
    }
    return n.isNeg = r,
    n
}
function biToBytes(i) {
    for (var t = "", r = biHighIndex(i); r > -1; --r)
        t += digitToBytes(i.digits[r]);
    return t
}
function digitToBytes(i) {
    var t = String.fromCharCode(255 & i);
    i >>>= 8;
    var r = String.fromCharCode(255 & i);
    return r + t
}
function biDump(i) {
    return (i.isNeg ? "-" : "") + i.digits.join(" ")
}
function biAdd(i, t) {
    var r;
    if (i.isNeg != t.isNeg)
        t.isNeg = !t.isNeg,
        r = biSubtract(i, t),
        t.isNeg = !t.isNeg;
    else {
        r = new BigInt;
        for (var e, n = 0, g = 0; g < i.digits.length; ++g)
            e = i.digits[g] + t.digits[g] + n,
            r.digits[g] = 65535 & e,
            n = Number(e >= biRadix);
        r.isNeg = i.isNeg
    }
    return r
}
function biSubtract(i, t) {
    var r;
    if (i.isNeg != t.isNeg)
        t.isNeg = !t.isNeg,
        r = biAdd(i, t),
        t.isNeg = !t.isNeg;
    else {
        r = new BigInt;
        var e, n;
        n = 0;
        for (var g = 0; g < i.digits.length; ++g)
            e = i.digits[g] - t.digits[g] + n,
            r.digits[g] = 65535 & e,
            r.digits[g] < 0 && (r.digits[g] += biRadix),
            n = 0 - Number(e < 0);
        if (n == -1) {
            n = 0;
            for (var g = 0; g < i.digits.length; ++g)
                e = 0 - r.digits[g] + n,
                r.digits[g] = 65535 & e,
                r.digits[g] < 0 && (r.digits[g] += biRadix),
                n = 0 - Number(e < 0);
            r.isNeg = !i.isNeg
        } else
            r.isNeg = i.isNeg
    }
    return r
}
function biHighIndex(i) {
    for (var t = i.digits.length - 1; t > 0 && 0 == i.digits[t]; )
        --t;
    return t
}
function biNumBits(i) {
    var t, r = biHighIndex(i), e = i.digits[r], n = (r + 1) * bitsPerDigit;
    for (t = n; t > n - bitsPerDigit && 0 == (32768 & e); --t)
        e <<= 1;
    return t
}
function biMultiply(i, t) {
    for (var r, e, n, g = new BigInt, s = biHighIndex(i), d = biHighIndex(t), o = 0; o <= d; ++o) {
        for (r = 0,
        n = o,
        j = 0; j <= s; ++j,
        ++n)
            e = g.digits[n] + i.digits[j] * t.digits[o] + r,
            g.digits[n] = e & maxDigitVal,
            r = e >>> biRadixBits;
        g.digits[o + s + 1] = r
    }
    return g.isNeg = i.isNeg != t.isNeg,
    g
}
function biMultiplyDigit(i, t) {
    var r, e, n;
    result = new BigInt,
    r = biHighIndex(i),
    e = 0;
    for (var g = 0; g <= r; ++g)
        n = result.digits[g] + i.digits[g] * t + e,
        result.digits[g] = n & maxDigitVal,
        e = n >>> biRadixBits;
    return result.digits[1 + r] = e,
    result
}
function arrayCopy(i, t, r, e, n) {
    for (var g = Math.min(t + n, i.length), s = t, d = e; s < g; ++s,
    ++d)
        r[d] = i[s]
}
function biShiftLeft(i, t) {
    var r = Math.floor(t / bitsPerDigit)
      , e = new BigInt;
    arrayCopy(i.digits, 0, e.digits, r, e.digits.length - r);
    for (var n = t % bitsPerDigit, g = bitsPerDigit - n, s = e.digits.length - 1, d = s - 1; s > 0; --s,
    --d)
        e.digits[s] = e.digits[s] << n & maxDigitVal | (e.digits[d] & highBitMasks[n]) >>> g;
    return e.digits[0] = e.digits[s] << n & maxDigitVal,
    e.isNeg = i.isNeg,
    e
}
function biShiftRight(i, t) {
    var r = Math.floor(t / bitsPerDigit)
      , e = new BigInt;
    arrayCopy(i.digits, r, e.digits, 0, i.digits.length - r);
    for (var n = t % bitsPerDigit, g = bitsPerDigit - n, s = 0, d = s + 1; s < e.digits.length - 1; ++s,
    ++d)
        e.digits[s] = e.digits[s] >>> n | (e.digits[d] & lowBitMasks[n]) << g;
    return e.digits[e.digits.length - 1] >>>= n,
    e.isNeg = i.isNeg,
    e
}
function biMultiplyByRadixPower(i, t) {
    var r = new BigInt;
    return arrayCopy(i.digits, 0, r.digits, t, r.digits.length - t),
    r
}
function biDivideByRadixPower(i, t) {
    var r = new BigInt;
    return arrayCopy(i.digits, t, r.digits, 0, r.digits.length - t),
    r
}
function biModuloByRadixPower(i, t) {
    var r = new BigInt;
    return arrayCopy(i.digits, 0, r.digits, 0, t),
    r
}
function biCompare(i, t) {
    if (i.isNeg != t.isNeg)
        return 1 - 2 * Number(i.isNeg);
    for (var r = i.digits.length - 1; r >= 0; --r)
        if (i.digits[r] != t.digits[r])
            return i.isNeg ? 1 - 2 * Number(i.digits[r] > t.digits[r]) : 1 - 2 * Number(i.digits[r] < t.digits[r]);
    return 0
}
function biDivideModulo(i, t) {
    var r, e, n = biNumBits(i), g = biNumBits(t), s = t.isNeg;
    if (n < g)
        return i.isNeg ? (r = biCopy(bigOne),
        r.isNeg = !t.isNeg,
        i.isNeg = !1,
        t.isNeg = !1,
        e = biSubtract(t, i),
        i.isNeg = !0,
        t.isNeg = s) : (r = new BigInt,
        e = biCopy(i)),
        new Array(r,e);
    r = new BigInt,
    e = i;
    for (var d = Math.ceil(g / bitsPerDigit) - 1, o = 0; t.digits[d] < biHalfRadix; )
        t = biShiftLeft(t, 1),
        ++o,
        ++g,
        d = Math.ceil(g / bitsPerDigit) - 1;
    e = biShiftLeft(e, o),
    n += o;
    for (var a = Math.ceil(n / bitsPerDigit) - 1, u = biMultiplyByRadixPower(t, a - d); biCompare(e, u) != -1; )
        ++r.digits[a - d],
        e = biSubtract(e, u);
    for (var b = a; b > d; --b) {
        var l = b >= e.digits.length ? 0 : e.digits[b]
          , h = b - 1 >= e.digits.length ? 0 : e.digits[b - 1]
          , f = b - 2 >= e.digits.length ? 0 : e.digits[b - 2]
          , c = d >= t.digits.length ? 0 : t.digits[d]
          , m = d - 1 >= t.digits.length ? 0 : t.digits[d - 1];
        l == c ? r.digits[b - d - 1] = maxDigitVal : r.digits[b - d - 1] = Math.floor((l * biRadix + h) / c);
        for (var x = r.digits[b - d - 1] * (c * biRadix + m), v = l * biRadixSquared + (h * biRadix + f); x > v; )
            --r.digits[b - d - 1],
            x = r.digits[b - d - 1] * (c * biRadix | m),
            v = l * biRadix * biRadix + (h * biRadix + f);
        u = biMultiplyByRadixPower(t, b - d - 1),
        e = biSubtract(e, biMultiplyDigit(u, r.digits[b - d - 1])),
        e.isNeg && (e = biAdd(e, u),
        --r.digits[b - d - 1])
    }
    return e = biShiftRight(e, o),
    r.isNeg = i.isNeg != s,
    i.isNeg && (r = s ? biAdd(r, bigOne) : biSubtract(r, bigOne),
    t = biShiftRight(t, o),
    e = biSubtract(t, e)),
    0 == e.digits[0] && 0 == biHighIndex(e) && (e.isNeg = !1),
    new Array(r,e)
}
function biDivide(i, t) {
    return biDivideModulo(i, t)[0]
}
function biModulo(i, t) {
    return biDivideModulo(i, t)[1]
}
function biMultiplyMod(i, t, r) {
    return biModulo(biMultiply(i, t), r)
}
function biPow(i, t) {
    for (var r = bigOne, e = i; ; ) {
        if (0 != (1 & t) && (r = biMultiply(r, e)),
        t >>= 1,
        0 == t)
            break;
        e = biMultiply(e, e)
    }
    return r
}
function biPowMod(i, t, r) {
    for (var e = bigOne, n = i, g = t; ; ) {
        if (0 != (1 & g.digits[0]) && (e = biMultiplyMod(e, n, r)),
        g = biShiftRight(g, 1),
        0 == g.digits[0] && 0 == biHighIndex(g))
            break;
        n = biMultiplyMod(n, n, r)
    }
    return e
}
function RSAKeyPair(i, t, r, e) {
    this.e = biFromHex(i),
    this.d = biFromHex(t),
    this.m = biFromHex(r),
    "number" != typeof e ? this.chunkSize = 2 * biHighIndex(this.m) : this.chunkSize = e / 8,
    this.radix = 16,
    this.barrett = new BarrettMu(this.m)
}
function encryptedString(i, t, r, e) {
    var n, g, s, d, o, a, u, b, l, h, f = new Array, c = t.length, m = "";
    for (d = "string" == typeof r ? r == RSAAPP.NoPadding ? 1 : r == RSAAPP.PKCS1Padding ? 2 : 0 : 0,
    o = "string" == typeof e && e == RSAAPP.RawEncoding ? 1 : 0,
    1 == d ? c > i.chunkSize && (c = i.chunkSize) : 2 == d && c > i.chunkSize - 11 && (c = i.chunkSize - 11),
    n = 0,
    g = 2 == d ? c - 1 : i.chunkSize - 1; n < c; )
        d ? f[g] = t.charCodeAt(n) : f[n] = t.charCodeAt(n),
        n++,
        g--;
    for (1 == d && (n = 0),
    g = i.chunkSize - c % i.chunkSize; g > 0; ) {
        if (2 == d) {
            for (a = Math.floor(256 * Math.random()); !a; )
                a = Math.floor(256 * Math.random());
            f[n] = a
        } else
            f[n] = 0;
        n++,
        g--
    }
    for (2 == d && (f[c] = 0,
    f[i.chunkSize - 2] = 2,
    f[i.chunkSize - 1] = 0),
    u = f.length,
    n = 0; n < u; n += i.chunkSize) {
        for (b = new BigInt,
        g = 0,
        s = n; s < n + i.chunkSize; ++g)
            b.digits[g] = f[s++],
            b.digits[g] += f[s++] << 8;
        l = i.barrett.powMod(b, i.e),
        h = 1 == o ? biToBytes(l) : 16 == i.radix ? biToHex(l) : biToString(l, i.radix),
        m += h
    }
    return m
}
function decryptedString(i, t) {
    var r, e, n, g, s = t.split(" "), d = "";
    for (e = 0; e < s.length; ++e)
        for (g = 16 == i.radix ? biFromHex(s[e]) : biFromString(s[e], i.radix),
        r = i.barrett.powMod(g, i.d),
        n = 0; n <= biHighIndex(r); ++n)
            d += String.fromCharCode(255 & r.digits[n], r.digits[n] >> 8);
    return 0 == d.charCodeAt(d.length - 1) && (d = d.substring(0, d.length - 1)),
    d
}
var biRadixBase = 2, biRadixBits = 16, bitsPerDigit = biRadixBits, biRadix = 65536, biHalfRadix = biRadix >>> 1, biRadixSquared = biRadix * biRadix, maxDigitVal = biRadix - 1, maxInteger = 9999999999999998, maxDigits, ZERO_ARRAY, bigZero, bigOne;
setMaxDigits(20);
var dpl10 = 15
  , lr10 = biFromNumber(1e15)
  , hexatrigesimalToChar = new Array("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z")
  , hexToChar = new Array("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f")
  , highBitMasks = new Array(0,32768,49152,57344,61440,63488,64512,65024,65280,65408,65472,65504,65520,65528,65532,65534,65535)
  , lowBitMasks = new Array(0,1,3,7,15,31,63,127,255,511,1023,2047,4095,8191,16383,32767,65535)
  , RSAAPP = {};
RSAAPP.NoPadding = "NoPadding",
RSAAPP.PKCS1Padding = "PKCS1Padding",
RSAAPP.RawEncoding = "RawEncoding",
RSAAPP.NumericEncoding = "NumericEncoding";

function enc_pwd_name(rsaString,username,pwd) {
                        var e = {};
                        setMaxDigits(131);
                        var c = new RSAKeyPair("3","10001",rsaString,1024);
			e.pwd  = q.encode(encryptedString(c, pwd, RSAAPP.PKCS1Padding, RSAAPP.RawEncoding));
                        e.username = q.encode(encryptedString(c, username, RSAAPP.PKCS1Padding, RSAAPP.RawEncoding));
                        return e
                    }