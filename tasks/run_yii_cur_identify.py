from task.yiigle.cur_identify import CurIdentify
if __name__ == '__main__':
    file_path = r'C:\Users\hello\Desktop\2023年提交数据\线粒体替代疗法的研究进展_2017年05月25日.pdf'
    c = CurIdentify()
    c.extract_text(file_path)