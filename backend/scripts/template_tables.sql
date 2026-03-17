-- =============================================
-- 文章模板系统数据库脚本
-- =============================================

-- 1. 创建文章模板表
CREATE TABLE IF NOT EXISTS article_templates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '模板ID',
    name VARCHAR(100) NOT NULL COMMENT '模板名称',
    description VARCHAR(500) DEFAULT NULL COMMENT '模板描述',
    thumbnail VARCHAR(500) DEFAULT NULL COMMENT '缩略图URL',
    styles JSON NOT NULL COMMENT '样式配置',
    is_system TINYINT(1) DEFAULT 0 COMMENT '是否系统预设',
    is_public TINYINT(1) DEFAULT 0 COMMENT '是否公开',
    user_id BIGINT DEFAULT NULL COMMENT '用户ID（自定义模板的所有者）',
    use_count INT DEFAULT 0 COMMENT '使用次数',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_is_system (is_system),
    INDEX idx_is_public (is_public),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文章模板表';

-- 2. 为 publish_records 表添加 rendered_content 字段（如果不存在）
-- 注意：如果字段已存在会报错，可以忽略
ALTER TABLE publish_records ADD COLUMN rendered_content TEXT COMMENT '渲染后的HTML内容' AFTER content;

-- 3. 插入5个系统预设模板
INSERT INTO article_templates (name, description, styles, is_system, is_public, user_id, use_count) VALUES

-- 模板1: 简约黑白
('简约黑白', '经典黑白配色，简洁大方，适合各类通用文章', '{
  "container": {
    "backgroundColor": "#ffffff",
    "padding": "20px",
    "maxWidth": "800px",
    "fontFamily": "-apple-system, BlinkMacSystemFont, ''PingFang SC'', ''Microsoft YaHei'', sans-serif"
  },
  "h1": {
    "color": "#333333",
    "fontSize": "24px",
    "fontWeight": "600",
    "marginBottom": "16px",
    "paddingBottom": "10px",
    "borderBottom": "2px solid #333333"
  },
  "h2": {
    "color": "#333333",
    "fontSize": "20px",
    "fontWeight": "600",
    "marginTop": "24px",
    "marginBottom": "12px",
    "paddingLeft": "12px",
    "borderLeft": "4px solid #333333"
  },
  "h3": {
    "color": "#333333",
    "fontSize": "18px",
    "fontWeight": "600",
    "marginTop": "20px",
    "marginBottom": "10px"
  },
  "p": {
    "color": "#333333",
    "fontSize": "16px",
    "lineHeight": "1.8",
    "marginBottom": "12px",
    "textAlign": "justify"
  },
  "blockquote": {
    "color": "#666666",
    "backgroundColor": "#f5f5f5",
    "fontSize": "15px",
    "padding": "12px 16px",
    "marginTop": "16px",
    "marginBottom": "16px",
    "borderLeft": "4px solid #333333",
    "borderRadius": "4px"
  },
  "ul": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "ol": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "li": {
    "color": "#333333",
    "fontSize": "15px",
    "lineHeight": "1.8",
    "marginBottom": "6px"
  },
  "code": {
    "color": "#333333",
    "backgroundColor": "#f0f0f0",
    "fontSize": "14px",
    "padding": "2px 6px",
    "borderRadius": "4px",
    "fontFamily": "Consolas, Monaco, monospace"
  },
  "pre": {
    "color": "#f8f8f2",
    "backgroundColor": "#2d2d2d",
    "padding": "16px",
    "borderRadius": "8px",
    "fontSize": "14px",
    "lineHeight": "1.6"
  },
  "a": {
    "color": "#333333",
    "textDecoration": "underline"
  },
  "img": {
    "maxWidth": "100%",
    "borderRadius": "8px",
    "marginTop": "16px",
    "marginBottom": "16px"
  },
  "hr": {
    "borderTop": "1px solid #e0e0e0",
    "marginTop": "24px",
    "marginBottom": "24px"
  },
  "strong": {
    "color": "#333333",
    "fontWeight": "600"
  },
  "em": {
    "color": "#333333",
    "fontStyle": "italic"
  }
}', 1, 1, NULL, 0),

-- 模板2: 微信绿
('微信绿', '微信原生风格，清新自然，适合公众号文章', '{
  "container": {
    "backgroundColor": "#ffffff",
    "padding": "20px",
    "maxWidth": "800px",
    "fontFamily": "-apple-system, BlinkMacSystemFont, ''PingFang SC'', ''Microsoft YaHei'', sans-serif"
  },
  "h1": {
    "color": "#07C160",
    "fontSize": "24px",
    "fontWeight": "600",
    "marginBottom": "16px",
    "paddingBottom": "10px",
    "borderBottom": "2px solid #07C160"
  },
  "h2": {
    "color": "#07C160",
    "fontSize": "20px",
    "fontWeight": "600",
    "marginTop": "24px",
    "marginBottom": "12px",
    "paddingLeft": "12px",
    "borderLeft": "4px solid #07C160"
  },
  "h3": {
    "color": "#07C160",
    "fontSize": "18px",
    "fontWeight": "600",
    "marginTop": "20px",
    "marginBottom": "10px"
  },
  "p": {
    "color": "#333333",
    "fontSize": "16px",
    "lineHeight": "1.8",
    "marginBottom": "12px",
    "textAlign": "justify"
  },
  "blockquote": {
    "color": "#666666",
    "backgroundColor": "#f0f9f4",
    "fontSize": "15px",
    "padding": "12px 16px",
    "marginTop": "16px",
    "marginBottom": "16px",
    "borderLeft": "4px solid #07C160",
    "borderRadius": "4px"
  },
  "ul": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "ol": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "li": {
    "color": "#333333",
    "fontSize": "15px",
    "lineHeight": "1.8",
    "marginBottom": "6px"
  },
  "code": {
    "color": "#07C160",
    "backgroundColor": "#f0f9f4",
    "fontSize": "14px",
    "padding": "2px 6px",
    "borderRadius": "4px",
    "fontFamily": "Consolas, Monaco, monospace"
  },
  "pre": {
    "color": "#f8f8f2",
    "backgroundColor": "#2d3748",
    "padding": "16px",
    "borderRadius": "8px",
    "fontSize": "14px",
    "lineHeight": "1.6"
  },
  "a": {
    "color": "#07C160",
    "textDecoration": "none"
  },
  "img": {
    "maxWidth": "100%",
    "borderRadius": "8px",
    "marginTop": "16px",
    "marginBottom": "16px"
  },
  "hr": {
    "borderTop": "1px solid #07C160",
    "marginTop": "24px",
    "marginBottom": "24px"
  },
  "strong": {
    "color": "#07C160",
    "fontWeight": "600"
  },
  "em": {
    "color": "#333333",
    "fontStyle": "italic"
  }
}', 1, 1, NULL, 0),

-- 模板3: 科技蓝
('科技蓝', '科技感蓝色主题，现代简约，适合技术和科技类文章', '{
  "container": {
    "backgroundColor": "#ffffff",
    "padding": "20px",
    "maxWidth": "800px",
    "fontFamily": "-apple-system, BlinkMacSystemFont, ''PingFang SC'', ''Microsoft YaHei'', sans-serif"
  },
  "h1": {
    "color": "#1890FF",
    "fontSize": "24px",
    "fontWeight": "600",
    "marginBottom": "16px",
    "paddingBottom": "10px",
    "borderBottom": "2px solid #1890FF"
  },
  "h2": {
    "color": "#1890FF",
    "fontSize": "20px",
    "fontWeight": "600",
    "marginTop": "24px",
    "marginBottom": "12px",
    "paddingLeft": "12px",
    "borderLeft": "4px solid #1890FF"
  },
  "h3": {
    "color": "#1890FF",
    "fontSize": "18px",
    "fontWeight": "600",
    "marginTop": "20px",
    "marginBottom": "10px"
  },
  "p": {
    "color": "#333333",
    "fontSize": "16px",
    "lineHeight": "1.8",
    "marginBottom": "12px",
    "textAlign": "justify"
  },
  "blockquote": {
    "color": "#666666",
    "backgroundColor": "#e6f7ff",
    "fontSize": "15px",
    "padding": "12px 16px",
    "marginTop": "16px",
    "marginBottom": "16px",
    "borderLeft": "4px solid #1890FF",
    "borderRadius": "4px"
  },
  "ul": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "ol": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "li": {
    "color": "#333333",
    "fontSize": "15px",
    "lineHeight": "1.8",
    "marginBottom": "6px"
  },
  "code": {
    "color": "#1890FF",
    "backgroundColor": "#e6f7ff",
    "fontSize": "14px",
    "padding": "2px 6px",
    "borderRadius": "4px",
    "fontFamily": "Consolas, Monaco, monospace"
  },
  "pre": {
    "color": "#abb2bf",
    "backgroundColor": "#282c34",
    "padding": "16px",
    "borderRadius": "8px",
    "fontSize": "14px",
    "lineHeight": "1.6"
  },
  "a": {
    "color": "#1890FF",
    "textDecoration": "none"
  },
  "img": {
    "maxWidth": "100%",
    "borderRadius": "8px",
    "marginTop": "16px",
    "marginBottom": "16px"
  },
  "hr": {
    "borderTop": "1px solid #1890FF",
    "marginTop": "24px",
    "marginBottom": "24px"
  },
  "strong": {
    "color": "#1890FF",
    "fontWeight": "600"
  },
  "em": {
    "color": "#333333",
    "fontStyle": "italic"
  }
}', 1, 1, NULL, 0),

-- 模板4: 暖橙活力
('暖橙活力', '活力橙色主题，热情醒目，适合营销推广和活动类文章', '{
  "container": {
    "backgroundColor": "#ffffff",
    "padding": "20px",
    "maxWidth": "800px",
    "fontFamily": "-apple-system, BlinkMacSystemFont, ''PingFang SC'', ''Microsoft YaHei'', sans-serif"
  },
  "h1": {
    "color": "#FF6A00",
    "fontSize": "24px",
    "fontWeight": "600",
    "marginBottom": "16px",
    "paddingBottom": "10px",
    "borderBottom": "2px solid #FF6A00"
  },
  "h2": {
    "color": "#FF6A00",
    "fontSize": "20px",
    "fontWeight": "600",
    "marginTop": "24px",
    "marginBottom": "12px",
    "paddingLeft": "12px",
    "borderLeft": "4px solid #FF6A00"
  },
  "h3": {
    "color": "#FF6A00",
    "fontSize": "18px",
    "fontWeight": "600",
    "marginTop": "20px",
    "marginBottom": "10px"
  },
  "p": {
    "color": "#333333",
    "fontSize": "16px",
    "lineHeight": "1.8",
    "marginBottom": "12px",
    "textAlign": "justify"
  },
  "blockquote": {
    "color": "#666666",
    "backgroundColor": "#fff7e6",
    "fontSize": "15px",
    "padding": "12px 16px",
    "marginTop": "16px",
    "marginBottom": "16px",
    "borderLeft": "4px solid #FF6A00",
    "borderRadius": "4px"
  },
  "ul": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "ol": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "li": {
    "color": "#333333",
    "fontSize": "15px",
    "lineHeight": "1.8",
    "marginBottom": "6px"
  },
  "code": {
    "color": "#FF6A00",
    "backgroundColor": "#fff7e6",
    "fontSize": "14px",
    "padding": "2px 6px",
    "borderRadius": "4px",
    "fontFamily": "Consolas, Monaco, monospace"
  },
  "pre": {
    "color": "#f8f8f2",
    "backgroundColor": "#2d2d2d",
    "padding": "16px",
    "borderRadius": "8px",
    "fontSize": "14px",
    "lineHeight": "1.6"
  },
  "a": {
    "color": "#FF6A00",
    "textDecoration": "none"
  },
  "img": {
    "maxWidth": "100%",
    "borderRadius": "8px",
    "marginTop": "16px",
    "marginBottom": "16px"
  },
  "hr": {
    "borderTop": "1px solid #FF6A00",
    "marginTop": "24px",
    "marginBottom": "24px"
  },
  "strong": {
    "color": "#FF6A00",
    "fontWeight": "600"
  },
  "em": {
    "color": "#333333",
    "fontStyle": "italic"
  }
}', 1, 1, NULL, 0),

-- 模板5: 文艺紫
('文艺紫', '优雅紫色主题，文艺气息，适合文化艺术和生活类文章', '{
  "container": {
    "backgroundColor": "#ffffff",
    "padding": "20px",
    "maxWidth": "800px",
    "fontFamily": "-apple-system, BlinkMacSystemFont, ''PingFang SC'', ''Microsoft YaHei'', sans-serif"
  },
  "h1": {
    "color": "#722ED1",
    "fontSize": "24px",
    "fontWeight": "600",
    "marginBottom": "16px",
    "paddingBottom": "10px",
    "borderBottom": "2px solid #722ED1"
  },
  "h2": {
    "color": "#722ED1",
    "fontSize": "20px",
    "fontWeight": "600",
    "marginTop": "24px",
    "marginBottom": "12px",
    "paddingLeft": "12px",
    "borderLeft": "4px solid #722ED1"
  },
  "h3": {
    "color": "#722ED1",
    "fontSize": "18px",
    "fontWeight": "600",
    "marginTop": "20px",
    "marginBottom": "10px"
  },
  "p": {
    "color": "#333333",
    "fontSize": "16px",
    "lineHeight": "1.8",
    "marginBottom": "12px",
    "textAlign": "justify"
  },
  "blockquote": {
    "color": "#666666",
    "backgroundColor": "#f9f0ff",
    "fontSize": "15px",
    "padding": "12px 16px",
    "marginTop": "16px",
    "marginBottom": "16px",
    "borderLeft": "4px solid #722ED1",
    "borderRadius": "4px"
  },
  "ul": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "ol": {
    "marginTop": "12px",
    "marginBottom": "12px",
    "paddingLeft": "24px"
  },
  "li": {
    "color": "#333333",
    "fontSize": "15px",
    "lineHeight": "1.8",
    "marginBottom": "6px"
  },
  "code": {
    "color": "#722ED1",
    "backgroundColor": "#f9f0ff",
    "fontSize": "14px",
    "padding": "2px 6px",
    "borderRadius": "4px",
    "fontFamily": "Consolas, Monaco, monospace"
  },
  "pre": {
    "color": "#f8f8f2",
    "backgroundColor": "#2d2a3e",
    "padding": "16px",
    "borderRadius": "8px",
    "fontSize": "14px",
    "lineHeight": "1.6"
  },
  "a": {
    "color": "#722ED1",
    "textDecoration": "none"
  },
  "img": {
    "maxWidth": "100%",
    "borderRadius": "8px",
    "marginTop": "16px",
    "marginBottom": "16px"
  },
  "hr": {
    "borderTop": "1px solid #722ED1",
    "marginTop": "24px",
    "marginBottom": "24px"
  },
  "strong": {
    "color": "#722ED1",
    "fontWeight": "600"
  },
  "em": {
    "color": "#333333",
    "fontStyle": "italic"
  }
}', 1, 1, NULL, 0);

-- 查看创建结果
SELECT id, name, description, is_system, is_public, use_count FROM article_templates;
