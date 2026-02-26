import requests
from bs4 import BeautifulSoup
import time

def get_repo_readme(repo_path, max_length=500):
    """
    根据仓库路径（如 'psf/requests'）获取 README 的纯文本
    """
    # 优先尝试 main 分支，不行再尝试 master
    for branch in ['main', 'master']:
        raw_url = f"https://raw.githubusercontent.com/{repo_path}/{branch}/README.md"
        try:
            resp = requests.get(raw_url, timeout=5)
            if resp.status_code == 200:
                # 只取前 500 个字符，防止内容过长
                return resp.text[:max_length].replace('\n', ' ')
        except:
            continue
    return "无法获取 README 内容"

def get_github_trending(since='daily', max_count=5, max_length=500):
    '''
    since = ['daily', 'weekly', 'monthly']
    '''
    url = f"https://github.com/trending?since={since}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        # 找到所有项目卡片
        articles = soup.select('article.Box-row')
        print(f"成功找到 {len(articles)} 个趋势项目，开始抓取详情...\n")

        for article in articles[:max_count]:
            title_tag = article.select_one('h2.h3 a')
            if not title_tag: continue
            
            repo_path = title_tag['href'].strip('/') # 得到 "user/repo"
            
            print(f"正在分析: {repo_path}...")
            readme_text = get_repo_readme(repo_path, max_length)
            
            results.append({
                'name': repo_path,
                'readme_summary': readme_text
            })
            
            # 💡 重要：抓取详情页之间稍微停一下，保护 IP
            time.sleep(3) 
            
        return results
    except Exception as e:
        print(f"发生错误: {e}")
        return []

if __name__ == "__main__":
    data = get_github_trending()
    for item in data:
        print(f"\n📦 项目: {item['name']}")
        print(f"📖 README 摘要: {item['readme_summary']}...")
        print("-" * 30)