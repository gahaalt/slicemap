# Quick Start

## Create, query and visualize SliceMap

```py
from slicemap import SliceMap

sm = SliceMap()

sm[-10:10] = 0
sm[2:4] = 1
sm[4:6] = 2
sm[7:9] = 3
sm[12:15] = 1.5
print(sm[2], sm[3], sm[4], sm[9], sm[15])
```

Outputs:

```
1 1 2 0 None
```

As long as you work with numerical values, you can do:

```
sm.plot()
```

![figure1](https://github.com/gahaalt/slicemap/blob/main/docs/figures/figure1.png?raw=true)

## Include `start` | `end`

The default value is `include="start"`, but you can choose to include the end of slices instead.

```py
from slicemap import SliceMap

sm1 = SliceMap(include="start")
sm1[2:3] = 1
sm1[3:4] = 2
sm1[4:5] = 3
print(sm1[3], sm1[4])

sm2 = SliceMap(include="end")
sm2[2:3] = 1
sm2[3:4] = 2
sm2[4:5] = 3
print(sm2[3], sm2[4])
```

Outputs:

```
2 3
1 2
```

## Query either values or ranges

You can equery each value individually, or query with a slice to get all values in given slice.

```py
from slicemap import SliceMap

sm = SliceMap(include="start")

sm[-10:10] = 0
sm[2:4] = 1
sm[4:6] = 2
sm[7:9] = 3
sm[12:15] = 1.5
print(sm[3], sm[5], sm[8])
print(sm[3:8])
```

Outputs:

```
1 2 3
(1, 2, 0, 3)
```

## More information

* Package `matplotlib` is an optional dependency - without it you can use the pacakge, but not the plotting
  functionality.
* You can use slices based on any number-like objects (except complex numbers) as keys. It'll work with ints,
  floats or numpy values.
* You can use any object as values.
