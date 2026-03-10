flowchart TB
    %% 定义样式类
    classDef domain fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef server fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef monitor fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px
    classDef github fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef data fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef expired fill:#ffebee,stroke:#c62828,stroke-width:2px,stroke-dasharray: 5 5

    %% 用户访问层
    subgraph Users["🌐 用户访问层"]
        CN[("国内用户")] --> CDN["Cloudflare CDN<br/>(免费版)"]
        OS[("海外用户")] --> R53["Route53<br/>智能解析"]
    end

    %% 域名层
    subgraph Domains["📝 域名层 (现有资源)"]
        TXDOMAIN["yourdomain.cn<br/>✅ 已备案<br/>(腾讯云解析)"]:::domain
        AWSDOMAIN["name.com<br/>🌐 未备案<br/>(Route53)"]:::domain
    end

    %% 主服务器层
    subgraph Servers["🖥️ 服务器集群 (4台)"]
        direction TB
        
        subgraph AWS["🟠 亚马逊云 (2核8G)<br/>⏰ 6个月到期 [2025-09]"]
            DD_AGENT1["Datadog Agent<br/>(全功能)"]:::monitor
            NEWRELIC["New Relic<br/>(GitHub Pack)"]:::github
            GRAFANA["Grafana<br/>(监控面板)"]:::monitor
            API["API 服务<br/>api.name.com"]:::server
            DD_LOGS["Datadog Log<br/>聚合中心"]:::monitor
        end
        
        subgraph TX["🔵 腾讯云 (2核2G)<br/>⏰ 11个月到期 [2026-02]<br/>⚠️ 300G/月流量限制"]
            DD_AGENT2["Datadog Agent<br/>(精简)"]:::monitor
            SENTRY["Sentry<br/>(错误追踪)"]:::github
            WEB["主站<br/>www.yourdomain.cn"]:::server
            PAGECLIP["Pageclip 表单<br/>(GitHub Pack)"]:::github
            CDN2["腾讯云 COS+CDN<br/>(静态资源)"]:::data
        end
        
        subgraph VOL["🟡 火山云 (2核2G)<br/>⏰ 5个月到期 [2025-08]<br/>⚠️ 1Mbps 带宽限制"]
            DD_AGENT3["Datadog Agent<br/>(仅指标)"]:::monitor
            ZYTE["Zyte 爬虫调度<br/>(Scrapyd)"]:::server
            MINIO["MinIO 对象存储<br/>(40G 临时存储)"]:::data
            POEDITOR["POEditor CLI<br/>(多语言同步)"]:::server
        end
        
        subgraph AZ["🟢 Azure (2核1G)<br/>⏰ 1年到期 [2026-03]<br/>✅ 长期锚点"]
            DD_AGENT4["Datadog Agent<br/>(基础)"]:::monitor
            CODESCENE["CodeScene<br/>(代码分析)"]:::github
            SIMPLE["Simple Analytics<br/>(自托管)"]:::github
            ONEPASS["1Password CLI<br/>(密钥中心)"]:::github
            LOKI["Loki 日志存储<br/>(60G 长期)"]:::data
            PG["PostgreSQL<br/>(配置中心)"]:::data
            BACKUP["备份接收中心<br/>(汇聚集群)"]:::data
        end
    end

    %% GitHub Pack 资源层
    subgraph GitHub["🎓 GitHub Student Pack 资源"]
        DO["DigitalOcean<br/>$100 额度<br/>(4个月备用机)"]:::github
        GH_COPILOT["GitHub Copilot<br/>(代码辅助)"]:::github
        DEEPNOTE["Deepnote Team<br/>(数据分析 SaaS)"]:::github
        POSTMAN["Postman Pro<br/>(API 测试)"]:::github
    end

    %% 流量走向
    CDN --> TXDOMAIN --> WEB
    R53 --> AWSDOMAIN --> API
    WEB --> CDN2
    
    %% 监控数据流向
    DD_AGENT1 & DD_AGENT2 & DD_AGENT3 & DD_AGENT4 -->|"Metrics"| DD_CLOUD["Datadog Cloud<br/>(学生版 10Agents)"]:::monitor
    DD_AGENT1 -->|"Logs"| DD_LOGS
    DD_LOGS -.->|"归档"| AZ
    SENTRY -->|"Errors"| SENTRY_CLOUD["Sentry Cloud<br/>(GitHub Pack)"]:::github
    
    %% 数据备份流向 (时间线)
    VOL -->|"每月1日<br/>全量备份"| BACKUP
    AWS -->|"每月1日<br/>配置导出"| BACKUP
    TX -->|"每周<br/>数据库备份"| BACKUP
    
    %% 过期迁移示意
    VOL -.->|"2025-08 到期<br/>数据迁移"| AZ
    AWS -.->|"2025-09 到期<br/>监控迁往"| AZ
    TX -.->|"2026-02 到期<br/>保留或续费"| TX
    
    %% 密钥管理
    ONEPASS -->|"密钥分发"| AWS & TX & VOL
    
    %% 爬虫数据流
    ZYTE -->|"调度任务"| ZYTE_CLOUD["Zyte Proxy<br/>(云代理池)"]
    ZYTE_CLOUD -->|"抓取结果"| MINIO
    MINIO -->|"定期同步"| BACKUP
    
    %% 域名策略补充
    subgraph DNS_Strategy["📋 域名子域规划"]
        TX_SUB["www.yourdomain.cn<br/>form.yourdomain.cn<br/>status.yourdomain.cn"]:::domain
        AWS_SUB["api.name.com<br/>grafana.name.com<br/>*.name.com"]:::domain
    end
    
    TXDOMAIN --- TX_SUB
    AWSDOMAIN --- AWS_SUB

    %% 流量保护机制
    subgraph Protection["🛡️ 流量保护机制 (腾讯云)"]
        ALERT1["Datadog 告警<br/>240G (80%)"]:::monitor
        ALERT2["自动熔断<br/>280G (93%)"]:::expired
        CDN2 -->|"分流"| ALERT1
    end
    
    WEB --> Protection

    %% 样式应用
    class AWS,VOL expired
