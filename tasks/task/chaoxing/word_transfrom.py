
class WordTrans():


    def is_alphabet(self,uchar):
        """判断一个unicode是否是半角英文字母"""
        if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
            return True
        else:
            return False

    def is_Qalphabet(self,uchar):
        """判断一个unicode是否是全角英文字母"""
        if (uchar >= u'\uff21' and uchar <= u'\uff3a') or (uchar >= u'\uff41' and uchar <= u'\uff5a'):
            return True
        else:
            return False

    def Q2B(self,uchar):
        """单个字符 全角转半角"""
        inside_code = ord(uchar)
        if inside_code == 0x3000:
            inside_code = 0x0020
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e: #转完之后不是半角字符返回原来的字符
            return uchar
        return chr(inside_code)
    def stringQ2B(self,ustring):
        """把字符串全角转半角"""
        return "".join([self.Q2B(uchar) for uchar in ustring])


    def is_number(self,uchar):
        """判断一个unicode是否是半角数字"""
        if uchar >= u'\u0030' and uchar <= u'\u0039':
            return True
        else:
            return False


    def is_Qnumber(self,uchar):
        """判断一个unicode是否是全角数字"""
        if uchar >= u'\uff10' and uchar <= u'\uff19':
            return True
        else:
            return False

    def stringpartQ2B(self,ustring):
        """把字符串中数字和字母全角转半角"""
        return "".join([self.Q2B(uchar) if self.is_Qnumber(uchar) or self.is_Qalphabet(uchar) else uchar for uchar in ustring])
