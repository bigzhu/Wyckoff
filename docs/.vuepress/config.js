import { defaultTheme } from '@vuepress/theme-default'
import { defineUserConfig } from 'vuepress'
import { viteBundler } from '@vuepress/bundler-vite'

export default defineUserConfig({
  lang: 'zh-CN',

  title: 'Wyckoff 读书笔记',
  description: '聪明的钱解读市场的工具',

  theme: defaultTheme({
    logo: 'https://vuejs.press/images/hero.png',

    navbar: [
      {
        text: '首页',
        link: '/',
      },
      {
        text: '第一章',
        link: '/第一章_聪明钱解读市场的工具/第一节_聪明钱的看盘顺序.md',
      },
    ],

    sidebar: [
      {
        text: '第一章 聪明钱解读市场的工具',
        collapsible: true,
        children: [
          '/第一章_聪明钱解读市场的工具/第一节_聪明钱的看盘顺序.md',
          '/第一章_聪明钱解读市场的工具/第二节_CM观察走势遵循的原则.md',
          '/第一章_聪明钱解读市场的工具/第三节_供求关系.md',
          '/第一章_聪明钱解读市场的工具/第四节_公众对支撑和阻力的误解.md',
          '/第一章_聪明钱解读市场的工具/第五节_如何识别供应和需求扩大.md',
          '/第一章_聪明钱解读市场的工具/第六节_牛市中怎么看出供应进场了.md',
          '/第一章_聪明钱解读市场的工具/第七节_因果关系.md',
          '/第一章_聪明钱解读市场的工具/第八节_努力和结果的关系.md',
          '/第一章_聪明钱解读市场的工具/第九节_总结.md',
        ],
      },
      {
        text: '第二章 怎么知道主力机构开始接盘了',
        collapsible: true,
        children: [
          '/第二章_怎么知道主力机构开始接盘了/第一节_熊市终止的市场行为.md',
          '/第二章_怎么知道主力机构开始接盘了/第二节_停止行为.md',
          '/第二章_怎么知道主力机构开始接盘了/第三节_吸筹的第二阶段.md',
          '/第二章_怎么知道主力机构开始接盘了/第四节_吸筹的第三阶段.md',
          '/第二章_怎么知道主力机构开始接盘了/第五节_进入牛市.md',
          '/第二章_怎么知道主力机构开始接盘了/第六节_吸筹过程的操作综合案例.md',
          '/第二章_怎么知道主力机构开始接盘了/第七节_熊市结束的另一种模式.md',
          '/第二章_怎么知道主力机构开始接盘了/第八节_震仓.md',
        ],
      },
      {
        text: '第三章 威氏逃顶策略',
        collapsible: true,
        children: [
          '/第三章_威氏逃顶策略/第一节_牛市到顶的信号.md',
        ],
      },
    ],
  }),

  bundler: viteBundler(),
})
