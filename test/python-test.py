def func(param1, param2):
    print(f"param1:{param1}")
    print(f"param2:{param2}")

func(1, 2)

func(1, param2=2)

func(param1=1, param2=2)
func(param2='b', param1='a')