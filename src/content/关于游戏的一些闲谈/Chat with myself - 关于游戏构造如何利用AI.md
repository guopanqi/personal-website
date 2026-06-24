```
$ uv run python - <<'PY'
from sincity.rules.progression import start_new_run, change_actor_pressure
state, rng = start_new_run(1)
change_actor_pressure(state, 99, 'lena')
owners = set(state.deck.action_card_owners.values())
print('lena_locked', state.party['lena'].pressure_locked)
print('lena_location', state.party['lena'].stress_location)
print('represented', 'lena' in owners)
print('companions', state.companion_actor_ids)
PY

lena_locked True
lena_location 酒吧
represented True
companions ['lena']
```
像这样的一个smoke test需要语言具备什么能力？如果比如说，就是我们现在加了一个，他压力过大的时候，他会在酒吧，然后我们就是要复现一下这样的情景来测试一下。这个代码其实是我用Python+raylib实现的，AI就能够自己去测试验证、查看输出，再进行修改。

- 它要求这个游戏框架是CLI下完备的，不需要依赖于一个外部的编辑器去编译（unity），报错（godot），并且启动过程足够快速（<3秒）。
- 这要求这个游戏架构下游戏状态是用数据组织起来的，是逻辑和渲染分离的，这样能够通过输入，测试，输出观察到这一点。
- 这要求这个语言有足够快的反馈循环，运行时语言帮助了这一点不需要编译，eval也帮助了这一点有这种eval的能力也就是输入一段代码，然后得到一些反馈。如果说语言没有这种能力，那他必须写一个单独的文件去调用其中的函数，然后观察它的实现，往往不够快速。
这个思想是我们从Garry的用AI来构建网站的方式里面得到的。网站它还可以用HTML去检测真实的交互元素。对于游戏来说不行，但是我们可以测试验证循环。（其实也可以用网站去组织，但是我觉得我有点担心它对于游戏的适用性不强。）
另外一个思想是IMGUI。
还有一个思想是“原型”，把游戏玩法和美术视觉单独去做原型迭代。
还有一个想法来源是DragonrubyGametookit，我觉得它真正让游戏制作者专注于游戏。

所以这些框架是思想的现实实现，我觉得我们现在的这个Python和Ray Lib和Ray GUI 它完成了这些功能，然后这个框架在导出web，在完成游戏的原型-手机测试的循环中不太好。但是它其实也挺好，因为如果没有新的思想，它一定可以变得更完善、更和谐、更精美，但和它最初的那个版本区别不大。

---

我之后实现了js+phaser，简单地实现了之后，我觉得我真正对于它有了一点了解。

---

[1] 我看了很多语言和框架，试图达成这一点，但选择太多了，不了解的也太多了，即时用上AI我还是觉得头脑混乱。我最终用的方法是选择最好的，但是也不追求穷举，对于一些小的事物，等它长大再说吧，这种方法我觉得也是生活中人们面对许多商品时采用的方法，在已知范围内最好的，远超平均水平的那一个。这样一个复杂的问题就变得简单了。
在另一个产品制造者的角度，首先你必须做到最好，然后要考虑的它有没有可能从一个小的用户群体扩展到足够大的用户群体？如果存在的话，那么它就是我们可以说它可能能有更多的用户和赚更多的钱。

比如说Lisp足够好，但是它可能没办法拓展。我觉得我做的游戏的方向，我们必须在 叙事和机制的融合、塑造故事和人物，情感调动 上面做到最好。我们面对非反应，喜欢故事的玩家，我相信这样的人很多，但是怎么触达，以后再想吧。

—
