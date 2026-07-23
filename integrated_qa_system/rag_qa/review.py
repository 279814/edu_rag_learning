import argparse


parse = argparse.ArgumentParser(description='hello world!')

parse.add_argument('input', help='输入')
parse.add_argument('--output', help='输出')
parse.add_argument('--verbose', action='store_true', help='是否显示详细信息')
parse.add_argument('--num', default=1, type=int, help='数量')

args = parse.parse_args()
print(args)

print(f'输入: {args.input}')
if args.output:
    print(f'输出: {args.output}')

if args.verbose:
    print(f'是否显示详细信息: {args.verbose}')

print(f'数量: {args.num}')


