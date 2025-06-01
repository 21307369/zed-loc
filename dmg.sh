#!/bin/bash

# 检查并创建必要的目标目录
if [ ! -d "target" ]; then
    mkdir -p "target"
    echo "创建 target 目录..."
fi

# 创建DMG函数
create_dmg() {
    local arch=$1
    local target_dir="zed/target/$arch/zed"
    local dmg_path="target/zed-$arch.dmg"

    echo "创建 $arch 架构的DMG..."
    
    # 清理并重建目录
    rm -rf $target_dir && mkdir -p $target_dir
    
    # 复制应用
    cp -R "./zed/target/$arch/release/bundle/osx/Zed Nightly.app" "$target_dir/Zed.app"
    
    # 可选：添加快捷方式
    ln -s /Applications $target_dir
    
    # 创建DMG
    hdiutil create -volname "zed_cn" -srcfolder $target_dir -ov -format UDZO $dmg_path
}

# 为两种架构创建DMG
create_dmg "aarch64-apple-darwin"
create_dmg "x86_64-apple-darwin"

echo "所有架构的DMG创建完成"