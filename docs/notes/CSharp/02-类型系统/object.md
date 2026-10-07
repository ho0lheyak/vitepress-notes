---
title: "object"
description: "介绍：C# 万物之父，用来做通用接口，容纳任意类型的返回值，代价是装箱拆箱。"
date: "2026-09-24"
tags: ["类型系统"]
---
介绍：C# 万物之父，用来做通用接口，容纳任意类型的返回值，代价是装箱拆箱。

`object` 是 C# 所有类型的**终极基类**（所有类、值类型都隐式继承 `object`）。 `GetValue` 要做到**兼容任意类型数组**（`int[]` / `string[]` / `double[]`），返回值类型没法写死成`int`或者`string`，所以统一返回`object`。

所有实例都可以向上转型为object。任何类型的实例都可以看作一个object（不管是值还是引用类型）


可以类比理解为c的void\*，
![object](/csharp/object.png)（这里不对应python的元类，即类的类父亲，c#也有元类是type）