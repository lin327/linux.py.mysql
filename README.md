``````mermaid
flowchart TB
    %% 样式定义 (兼容 GitHub 深色/浅色主题)
    classDef user fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000
    classDef domain fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#000
    classDef aws fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef tx fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
    classDef vol fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    classDef azure fill:#f3e5f5,stroke:#6a1b9a,stroke-width:3px,color:#000
    classDef monitor fill:#e0f2f1,stroke:#00695c,stroke-width:2px,color:#000
    classDef github fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#000
    classDef data fill:#fff8e1,stroke:#ff8f00,stroke-width:2px,color:#000
    
    %% 用户访问层
    User([👥 用户访问]):::user --> Route{智能路由}
    Route -->|国内流量| CN[🇨🇳 中国大陆]:::user
    Route -->|海外流量| OS[🌍 海外用户]:::user
    
    %% 域名层 (现有资源)
    CN --> TXDomain[yourdomain.cn<br/>✅ 已完成ICP备案<br/>腾讯云解析]:::domain
    OS --> AWSDomain[name.com<br/>🌐 未备案海外域名<br/>Route53解析]:::domain
    
    %% 四服务器集群 (核心)
    subgraph Cluster["🖥️ 四云服务器集群 (2025-2026)"]
        direction TB
        
        subgraph AWS["🟠 AWS 亚马逊云 (2核8G)<br/>⏰ 6个月到期 [2025-09]<br/>⚠️ 需迁移"]
            APISrv[api.name.com<br/>Grafana监控面板<br/>Datadog日志中心]:::aws
            DD_AWS[Datadog Agent<br/>(APM+Logs+Network)]:::monitor
            NewRelic[New Relic<br/>GitHub Student Pack]:::github
        end
        
        subgraph TX["🔵 腾讯云 (2核2G 4Mbps)<br/>⏰ 11个月到期 [2026-02]<br/>⚠️ 300G/月流量限制"]
            WebSrv[www.yourdomain.cn<br/>主站+Pageclip表单]:::tx
            DD_TX[Datadog Agent<br/>(精简模式+RUM)]:::monitor
            Sentry[Sentry<br/>错误追踪]:::github
            CDN[腾讯云COS<br/>+CDN加速]:::data
        end
        
        subgraph VOL["🟡 火山云 (2核2G 1Mbps)<br/>⏰ 5个月到期 [2025-08]<br/>⚠️ 低带宽限制"]
            Crawler[Zyte爬虫调度<br/>MinIO对象存储]:::vol
            DD_VOL[Datadog Agent<br/>(仅系统指标)]:::monitor
            POEditor[POEditor CLI<br/>多语言管理]:::github
        end
        
        subgraph AZURE["🟢 Azure (2核1G 60G)<br/>✅ 1年到期 [2026-03]<br/>🏠 长期锚点"]
            CodeScene[CodeScene<br/>代码质量分析]:::github
            OnePass[1Password CLI<br/>密钥管理中心]:::github
            Simple[Simple Analytics<br/>自托管版]:::github
            Backup[(📦 备份中心<br/>Loki日志+PostgreSQL<br/>60G长期存储)]:::azure
        end
    end
    
    %% GitHub Student Pack 资源
    subgraph GitHubRes["🎓 GitHub Student Pack 资源"]
        DO[DigitalOcean<br/>$100额度<br/>备用节点]:::github
        Deepnote[Deepnote Team<br/>数据分析SaaS]:::github
        Copilot[GitHub Copilot<br/>AI代码辅助]:::github
        Postman[Postman Pro<br/>API测试]:::github
    end
    
    %% 核心连接 (实线=活跃流量)
    TXDomain --> WebSrv
    AWSDomain --> APISrv
    WebSrv --> CDN
    
    %% 监控体系 (所有节点上报)
    DD_AWS & DD_TX & DD_VOL --> DDCloud[(Datadog Cloud<br/>学生版免费<br/>10Agents)]:::monitor
    Sentry --> SentryCloud[(Sentry Cloud<br/>50K errors/月)]:::github
    
    %% 数据备份流向 (虚线=归档/迁移)
    AWS -.->|每月1日<br/>配置导出| Backup
    VOL -.->|每月1日<br/>全量备份| Backup
    TX -.->|每周<br/>数据库备份| Backup
    
    %% 到期迁移路径 (红色虚线)
    VOL -.->|2025-08到期<br/>数据迁移| AZURE
    AWS -.->|2025-09到期<br/>监控迁移| AZURE
    
    %% 密钥管理 (点线=配置分发)
    OnePass -.->|密钥分发| AWS
    OnePass -.->|密钥分发| TX
    OnePass -.->|密钥分发| VOL
    
    %% 流量保护 (腾讯云)
    WebSrv --> Protection{流量保护}
    Protection -->|240G告警| Alert1[⚠️ Datadog告警]:::monitor
    Protection -->|280G熔断| Alert2[🛑 自动停止服务]:::data
    
    %% 样式覆盖
    style Cluster fill:#fafafa,stroke:#666,stroke-width:2px
    style GitHubRes fill:#f5f5f5,stroke:#666,stroke-width:2px
    style Protection fill:#ffebee,stroke:#c62828,stroke-width:2px
```mermaid
