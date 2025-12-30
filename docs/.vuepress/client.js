import { defineClientConfig } from 'vuepress/client'
import { defineMermaidConfig } from '@vuepress/plugin-markdown-chart/client'

export default defineClientConfig({
    enhance() {
        defineMermaidConfig({
            theme: 'base',
            themeVariables: {
                primaryColor: 'var(--mermaid-primary-bg)',
                primaryBorderColor: 'var(--mermaid-border)',
                primaryTextColor: 'var(--mermaid-text)',
                lineColor: 'var(--mermaid-border)',
                edgeLabelBackground: 'var(--mermaid-edge-bg)',
                tertiaryColor: 'var(--mermaid-secondary-bg)',
                fontSize: '14px',
                darkMode: false, // 我们通过 CSS 变量控制，不使用 mermaid 的内建暗色模式转换
            },
        })
    },
})
