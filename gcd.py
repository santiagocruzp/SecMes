# finding greatest common denominator function

def gcd(a,b):
    while a != 0:
        a,b = b%a, a
    return b

def main():
    flag = 0
    output = 0
    while flag == 0:
        x = int(input("input the first integer, or 0 to quit: "))
        if x == 0:
            flag = 1
            break
        elif x != 0:
            y = int(input("input a second integer: "))
            output = gcd(x,y)
            print(f"The greatest common denominator of {x} and {y} is {output}.")

if __name__ == "__main__":
    main()