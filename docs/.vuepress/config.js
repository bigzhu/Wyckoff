import { defaultTheme } from '@vuepress/theme-default'
import { defineUserConfig } from 'vuepress'
import { viteBundler } from '@vuepress/bundler-vite'
import { searchPlugin } from '@vuepress/plugin-search'
import fs from 'node:fs'
import path from 'node:path'
import { markdownChartPlugin } from '@vuepress/plugin-markdown-chart'

// 辅助函数：将中文数字转换为阿拉伯数字用于排序
const cnToNum = (str) => {
  const map = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
  };
  // 提取"第X节"或"第X章"中的数字
  const match = str.match(/第([一二三四五六七八九十]+)[节章]/);
  if (match) {
    let num = 0;
    const s = match[1];
    if (s.length === 1) return map[s] || 99;
    if (s.length === 2 && s.startsWith('十')) return 10 + (map[s[1]] || 0);
    // 简单处理常见的十几
    return 99;
  }
  return 99;
};

// 动态生成侧边栏
const getSidebar = () => {
  const docsDir = path.resolve(__dirname, '..');
  const sidebar = [];

  // 1. 前言
  if (fs.existsSync(path.join(docsDir, '前言.md'))) {
    sidebar.push('/前言.md');
  }

  // 获取所有内容，并筛选出章节子目录
  const items = fs.readdirSync(docsDir).filter(item => {
    return fs.statSync(path.join(docsDir, item)).isDirectory() &&
      !item.startsWith('.') &&
      !item.startsWith('wyckoff_content');
  });

  // 对章节目录进行排序
  items.sort((a, b) => cnToNum(a) - cnToNum(b));

  for (const item of items) {
    let text = item.replace(/_/g, ' ');

    const itemPath = path.join(docsDir, item);
    const children = fs.readdirSync(itemPath)
      .filter(f => f.endsWith('.md') && f !== 'README.md')
      .sort((a, b) => cnToNum(a) - cnToNum(b))
      .map(f => `/${item}/${f}`);

    if (children.length > 0) {
      sidebar.push({
        text,
        collapsible: true,
        children
      });
    }
  }

  // 2. 后记
  if (fs.existsSync(path.join(docsDir, '后记_交易哲学与实战心得.md'))) {
    sidebar.push('/后记_交易哲学与实战心得.md');
  }

  // 获取根目录下的 markdown 文件（排除 README, get-started, 前言, 后记）
  const rootFiles = fs.readdirSync(docsDir).filter(f => {
    return f.endsWith('.md') &&
      !['README.md', 'get-started.md', '前言.md', '后记_交易哲学与实战心得.md'].includes(f);
  });

  if (rootFiles.length > 0) {
    sidebar.push({
      text: '补充内容',
      collapsible: false,
      children: rootFiles.map(f => `/${f}`)
    });
  }

  return sidebar;
};

export default defineUserConfig({
  lang: 'zh-CN',
  base: '/Wyckoff/',

  title: 'Wyckoff 读书笔记',
  description: '聪明的钱解读市场的工具',

  head: [
    ['link', { rel: 'icon', href: '/Wyckoff/logo.png' }]
  ],

  theme: defaultTheme({
    logo: '/logo.png',

    navbar: [
      {
        text: '首页',
        link: '/',
      },
      {
        text: '术语速查',
        link: '/术语速查手册.md',
      },
      {
        text: '第一章',
        link: '/第一章_聪明钱解读市场的工具/第一节_聪明钱的看盘顺序.md',
      },
    ],

    // 使用动态生成的侧边栏
    sidebar: getSidebar(),

    lastUpdated: true,
    lastUpdatedText: '上次更新',
    contributors: true,
    contributorsText: '贡献者',
    editLink: true,
    editLinkText: '在 GitHub 上编辑此页',
    docsRepo: 'https://github.com/bigzhu/Wyckoff',
    docsBranch: 'main',
    docsDir: 'docs',
  }),

  plugins: [
    searchPlugin({
      locales: {
        '/': {
          placeholder: '搜索',
        },
      },
    }),
    markdownChartPlugin({
      mermaid: true,
    }),
  ],

  bundler: viteBundler(),
})
