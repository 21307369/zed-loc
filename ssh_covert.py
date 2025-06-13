import json
import os
import re
import logging

def parse_ssh_config(config_path):
    """解析SSH配置文件，返回Host配置列表"""
    logging.basicConfig(level=logging.DEBUG)
    hosts = []
    current_host = None
    
    try:
        logging.debug(f"开始解析SSH配置文件: {config_path}")
        with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                orig_line = line
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                    
                # print(f"行 {line_num}: 处理: {orig_line.strip()}")                
                # 匹配Host块开始
                if line.lower().startswith('host '):
                    if current_host:
                        hosts.append(current_host)
                    else:
                        logging.debug("没有当前Host块可保存")
                    
                    # 提取Host名称，保留完整名称（支持多个空格和通配符）
                    host_name = line[4:].strip()
                    # 如果Host名称为空，使用默认值
                    if not host_name:
                        host_name = 'unknown'
                    
                    current_host = {
                        'name': host_name,
                        'config': {}
                    }
                    continue
                    
                # 处理配置项
                if current_host:
                    parts = line.split(maxsplit=1)
                    if len(parts) == 2:
                        key, value = parts
                        current_host['config'][key] = value.strip()
                        logging.debug(f"添加配置项: {key} = {value.strip()}")
                    else:
                        logging.debug(f"无法解析配置行: {line}")
    except FileNotFoundError:
        logging.error(f"配置文件未找到: {config_path}")
        raise
    except PermissionError:
        logging.error(f"没有权限读取配置文件: {config_path}")
        raise
    except Exception as e:
        logging.error(f"解析配置文件时出错: {str(e)}")
        raise
    
    # 添加最后一个Host块
    if current_host:
        print(f"保存最后一个Host块: {current_host['name']}")
        hosts.append(current_host)
        
        # 添加最后一个Host块
    
    # 确保返回前添加最后一个Host块
    if current_host and current_host not in hosts:
        print(f"保存最后一个Host块: {current_host['name']}")
        hosts.append(current_host)
    
    print(f"解析完成，共找到 {len(hosts)} 个Host配置")
    for i, host in enumerate(hosts):
        print(f"Host {i+1}: {host['name']} - {host['config']}")
    
    return hosts

def convert_to_zed_json(hosts):
    """将解析的Host配置转换为Zed JSON格式"""
    ssh_connections = []
    
    for host in hosts:
        host_config = host['config']
        
        # 构建连接配置
        connection = {
            "nickname": host['name'],
            "host": host_config.get('HostName', ''),
            "username": host_config.get('User', ''),
            # "port": int(host_config.get('Port', '22')),  # 添加port字段并处理默认值
            "username": host_config.get('User', ''),
            "args": [],
            "projects": [],
            "upload_binary_over_ssh": True
        }
        
        # 处理IdentityFile
        identity_file = host_config.get('IdentityFile')
        if identity_file:
            connection["args"] = ["-i", os.path.expanduser(identity_file)]
        
        if not connection["host"]:
            print(f"警告: Host {host['name']} 缺少 HostName，已跳过")
            continue
            
        ssh_connections.append(connection)
    
    return {"ssh_connections": ssh_connections}

def main():
    """主函数"""
    # 使用测试配置文件（确保文件存在）
    config_path = os.path.join(os.path.dirname(__file__), '/Users/lsmir2/.ssh/config')
    print(f"使用配置文件: {config_path}")
    
    if not os.path.exists(config_path):
        print(f"错误: SSH配置文件不存在 - {config_path}")
        return
    
    try:
        # 解析配置文件
        hosts = parse_ssh_config(config_path)
        
        # 检查解析结果
        if not hosts:
            print("警告: 未解析到任何Host配置")
            return
        
        # 转换格式
        result = convert_to_zed_json(hosts)
        
        # 输出结果
        output_path = os.path.join(os.path.dirname(__file__), 'ssh_connections.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"成功转换 {len(result['ssh_connections'])} 个SSH连接配置")
        print(f"输出文件: {output_path}")
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()