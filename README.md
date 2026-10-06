# ulearning-quiz

## 项目简介
本项目适用于优学院作业板块中的测验，可以辅助计算“公式计算题”的答案和评判任何题型作答内容的正误。

## 使用方法
1.先使用“示例文件.json”来测试本地是否能够正常运行两个程序。

2.在测验页面抓取响应内容（F12），复制或下载到“示例文件.json”。

3.运行“calculate_answers.py”程序，即可显示出“公式计算题”的答案，非此类题目会跳过。

4.运行“evalculate_answers.py”程序，程序通过将json中studentAnswer下的score与题目的score对比，评判作答内容的正误。
