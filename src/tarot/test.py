from termcolor import colored

colors = ["grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
attrs = ["bold", "dark", "underline", "blink", "reverse", "concealed"]

for i, color in enumerate(colors):
    for j, attr in enumerate(attrs):
        print(colored(f"Hello, World! {color} {attr}", color, attrs=[attr]))
    print("="*60)
    print()

