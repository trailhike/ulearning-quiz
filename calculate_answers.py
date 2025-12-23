import json
import math
import re

# 数学函数映射，将公式中的函数名转换为 Python 中的函数
math_func_map = {
    'sqrt': 'sqrt',
    'atan': 'atan',
    'cos': 'cos',
    'sin': 'sin',
    'tan': 'tan',
    'log': 'log',
    'log10': 'log10',
    'exp': 'exp',
    'pi': 'pi',
    'pow': 'pow'
}

def evaluate_formula(formula, var_dict):
    """
    根据给定的变量字典 var_dict 和公式字符串 formula 计算结果
    """
    # 首先替换数学函数，确保函数名不会被变量替换影响
    for math_func, py_func in math_func_map.items():
        # 使用正则表达式只替换独立的函数名（后面跟着括号）
        pattern = r'\b' + re.escape(math_func) + r'\('
        formula = re.sub(pattern, f'math.{math_func}(', formula)
    
    # 然后替换变量名，使用正则表达式确保只替换独立的变量名
    for var_name, var_value in var_dict.items():
        # 使用正则表达式替换独立的变量名（前后不是字母数字或下划线）
        pattern = r'\b' + re.escape(var_name) + r'\b'
        formula = re.sub(pattern, str(var_value), formula)
    
    # 将 ^ 替换为 **（如果公式中包含幂运算）
    formula = formula.replace('^', '**')
    
    try:
        # 使用 eval 计算结果，注意安全风险，此处数据来自受信文件
        result = eval(formula, {"__builtins__": {}}, {"math": math})
        return result
    except Exception as e:
        print(f"计算公式时出错: {formula}, 错误: {e}")
        return None

def round_by_precision(value, precision):
    """
    根据精度要求四舍五入
    precision: 0.01 表示保留两位小数，0.1 表示保留一位小数，1 表示取整
    """
    if precision == 0.01:
        return round(value, 2)
    elif precision == 0.1:
        return round(value, 1)
    elif precision == 1:
        return round(value)
    else:
        # 如果精度值是一个字符串，尝试转换为浮点数
        try:
            prec = float(precision)
            if prec < 1:
                decimal_places = -int(math.log10(prec))
                return round(value, decimal_places)
            else:
                return round(value)
        except:
            return round(value, 2)  # 默认保留两位小数

def process_question(question):
    """
    处理单个题目
    """
    question_id = question.get('questionID')
    correct_answers = question.get('correctAnswer', [])
    formula_vars = question.get('formulaVar', [])

    # 检查formulaVar是否为null或空
    if formula_vars is None:
        print(f"跳过问题 {question_id}: formulaVar 为 null")
        return None
    
    # 构建变量字典
    var_dict = {}
    for var in formula_vars:
        var_name = var.get('name')
        var_value = var.get('value')
        if var_name is not None and var_value is not None:
            var_dict[var_name] = var_value
    
    print(f"\n题目 ID: {question_id}")
    print(f"变量赋值: {var_dict}")
    
    results = []
    for idx, answer in enumerate(correct_answers, 1):
        formula = answer.get('formula')
        blank_index = answer.get('blankIndex')
        precision = answer.get('precision')
        
        # 处理blankIndex：如果不是整数，则使用当前索引作为空格名
        try:
            # 尝试转换为数值
            blank_value = float(str(blank_index))
            if blank_value.is_integer():
                display_index = str(int(blank_value))
            else:
                display_index = f"{idx}"
        except:
            # 如果转换失败，使用当前索引
            display_index = f"{idx}"
        
        if formula:
            # 计算原始结果
            raw_value = evaluate_formula(formula, var_dict)
            if raw_value is not None:
                # 根据精度四舍五入
                rounded_value = round_by_precision(raw_value, precision)
                
                # 创建结果字典
                result_info = {
                    'original_blankIndex': blank_index,
                    'display_index': display_index,
                    'formula': formula,
                    'raw_value': raw_value,
                    'precision': precision,
                    'rounded_value': rounded_value,
                    'position': idx
                }
                results.append(result_info)
                
                # 显示替换后的公式用于调试
                debug_formula = formula
                for var_name, var_value in var_dict.items():
                    # 显示变量替换
                    pattern = r'\b' + re.escape(var_name) + r'\b'
                    debug_formula = re.sub(pattern, str(var_value), debug_formula)
                
                print(f"  空格 {display_index} :")
                print(f"    原始公式: {formula}")
                print(f"    计算结果: {raw_value:.6f} → {rounded_value}")
    
    return {
        'questionID': question_id,
        'var_dict': var_dict,
        'answers': results
    }

def main():
    # 读取 JSON 文件
    file_path = '示例文件.json'  # 替换为你的文件路径
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return
    
    # 提取题目列表
    questions = data.get('result', [])
    
    print("开始处理题目...")
    all_results = []
    skipped_questions = 0

    for question in questions:
        result = process_question(question)
        if result is not None:
            all_results.append(result)
        else:
            skipped_questions += 1
    
    # 可选：将结果保存到文件
    output_file = '计算结果.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n处理完成！")
    print(f"总题目数: {len(questions)}")
    print(f"成功处理: {len(all_results)}")
    print(f"跳过题目: {skipped_questions}")
    print(f"结果已保存到 {output_file}")
    
    # 输出汇总
    print("\n=== 结果汇总 ===")
    for result in all_results:
        print(f"\n题目 ID: {result['questionID']}")
        for answer in result['answers']:
            print(f"  {answer['display_index']}: {answer['rounded_value']}")

if __name__ == "__main__":
    main()