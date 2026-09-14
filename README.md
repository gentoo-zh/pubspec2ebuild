# pubspec2ebuild

把 `pubspec.lock` 变成 [gentoo-zh/overlay](https://github.com/gentoo-zh/overlay) `dart-pub.eclass` 读的 `PUB_HOSTED` 和 `PUB_GIT` 数组，定位同 pycargoebuild 之于 `cargo.eclass`。

```bash
pip install git+https://github.com/gentoo-zh/pubspec2ebuild
pubspec2ebuild path/to/pubspec.lock          # 打印两个数组，贴进 ebuild
pubspec2ebuild --urls path/to/pubspec.lock   # 打印每个包的 distfile URL
```

输入是 `flutter pub get` 写出的锁文件；pub workspace 的锁在 workspace 根目录。pub 的四种 source 里，`path` 随项目源码走、`sdk` 随 Flutter SDK 走，都不出现在数组里；别的 source 值直接报错。

限制：hosted 包只认 pub.dev（eclass 的缓存布局和 archive URL 都按 pub.dev 写）；git 包只认 GitHub（eclass 抓 GitHub archive）。碰到别的直接报错，不生成错的 SRC_URI。

```bash
python -m unittest discover -s tests
```
