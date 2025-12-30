import { defineClientConfig } from 'vuepress/client'
import { defineMermaidConfig } from '@vuepress/plugin-markdown-chart/client'

export default defineClientConfig({
    enhance() {
        defineMermaidConfig({
            theme: 'base',
            themeVariables: {
                primaryColor: '#f0f9f4',
                primaryBorderColor: '#3eaf7c',
                primaryTextColor: '#2c3e50',
                lineColor: '#3eaf7c',
                edgeLabelBackground: '#ffffff',
                tertiaryColor: '#f3f4f5',
                fontSize: '14px',
            },
        })
    },
})
