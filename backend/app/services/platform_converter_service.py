"""
多平台内容转换服务
将已有内容智能转换为不同平台格式
"""
import json
import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from app.schemas.platform_converter import (
    TargetPlatform,
    PlatformInfo,
    ConvertRequest,
    ConvertResult,
    BatchConvertRequest,
    BatchConvertResult,
)
from app.models.creation import Creation, CreationType, CreationStatus

logger = logging.getLogger(__name__)


class PlatformConverterService:
    """多平台内容转换服务"""
    
    # 平台配置
    PLATFORMS = {
        TargetPlatform.WECHAT: PlatformInfo(
            code="wechat_article",
            name="微信公众号",
            icon="wechat",
            max_length=20000,
            features=["支持长文", "强调深度", "注重排版"],
            tips=["使用小标题分隔", "添加引用增加权威性", "结尾引导关注"],
        ),
        TargetPlatform.XIAOHONGSHU: PlatformInfo(
            code="xiaohongshu_note",
            name="小红书",
            icon="xiaohongshu",
            max_length=1000,
            features=["短平快", "大量emoji", "种草向"],
            tips=["标题要有emoji", "分段要短", "多用感叹号", "添加话题标签"],
        ),
        TargetPlatform.DOUYIN: PlatformInfo(
            code="video_script",
            name="抖音脚本",
            icon="douyin",
            max_length=500,
            features=["口语化", "节奏快", "有钩子"],
            tips=["开头3秒抓眼球", "语言要口语化", "结尾引导互动"],
        ),
        TargetPlatform.ZHIHU: PlatformInfo(
            code="zhihu_answer",
            name="知乎回答",
            icon="zhihu",
            max_length=50000,
            features=["专业深度", "逻辑清晰", "数据支撑"],
            tips=["先亮观点", "分点论述", "引用数据和案例"],
        ),
        TargetPlatform.WEIBO: PlatformInfo(
            code="weibo_post",
            name="微博",
            icon="weibo",
            max_length=2000,
            features=["话题性强", "互动导向", "热点敏感"],
            tips=["添加话题标签", "@相关账号", "引导转发评论"],
        ),
        TargetPlatform.TOUTIAO: PlatformInfo(
            code="toutiao_article",
            name="今日头条",
            icon="toutiao",
            max_length=30000,
            features=["标题党", "信息量大", "接地气"],
            tips=["标题要吸睛", "多分段", "配图要多"],
        ),
        TargetPlatform.BILIBILI: PlatformInfo(
            code="bilibili_dynamic",
            name="B站动态",
            icon="bilibili",
            max_length=2000,
            features=["年轻化", "玩梗", "互动强"],
            tips=["可以玩梗", "语气轻松", "引导三连"],
        ),
    }
    
    # 平台对应的 CreationType
    PLATFORM_TO_CREATION_TYPE = {
        TargetPlatform.WECHAT: CreationType.WECHAT_ARTICLE,
        TargetPlatform.XIAOHONGSHU: CreationType.XIAOHONGSHU_NOTE,
        TargetPlatform.DOUYIN: CreationType.VIDEO_SCRIPT,
        TargetPlatform.ZHIHU: CreationType.WECHAT_ARTICLE,  # 复用
        TargetPlatform.WEIBO: CreationType.MARKETING_COPY,  # 复用
        TargetPlatform.TOUTIAO: CreationType.NEWS_ARTICLE,  # 复用
        TargetPlatform.BILIBILI: CreationType.MARKETING_COPY,  # 复用
    }
    
    @classmethod
    def get_platforms(cls) -> List[PlatformInfo]:
        """获取支持的平台列表"""
        return list(cls.PLATFORMS.values())
    
    @classmethod
    def get_platform_info(cls, platform: TargetPlatform) -> PlatformInfo:
        """获取平台信息"""
        return cls.PLATFORMS.get(platform)
    
    @classmethod
    async def convert(
        cls,
        request: ConvertRequest,
        db: Session,
        user_id: int,
        ai_model=None,
    ) -> ConvertResult:
        """
        转换内容到目标平台
        
        Args:
            request: 转换请求
            db: 数据库会话
            user_id: 用户ID
            ai_model: AI模型配置
            
        Returns:
            ConvertResult
        """
        # 获取原创作记录
        original = db.query(Creation).filter(
            Creation.id == request.creation_id,
            Creation.user_id == user_id,
        ).first()
        
        if not original:
            raise ValueError("创作记录不存在")
        
        original_content = original.output_content or ""
        original_title = original.title or ""
        original_platform = original.tool_type or original.creation_type.value
        
        # 获取目标平台信息
        target_info = cls.PLATFORMS.get(request.target_platform)
        if not target_info:
            raise ValueError(f"不支持的目标平台: {request.target_platform}")
        
        # 构建转换 prompt
        prompt = cls._build_convert_prompt(
            original_content=original_content,
            original_title=original_title,
            original_platform=original_platform,
            target_platform=request.target_platform,
            target_info=target_info,
            style_adjustment=request.style_adjustment,
            keep_structure=request.keep_structure,
            add_emojis=request.add_emojis,
            generate_tags=request.generate_tags,
        )
        
        # 调用 AI 进行转换
        from app.services.langchain import LangChainService
        
        try:
            if ai_model:
                service = LangChainService(
                    provider=ai_model.provider,
                    model=ai_model.model_name or "gpt-4",
                    api_key=ai_model.api_key,
                    api_base=ai_model.base_url,
                )
            else:
                service = LangChainService(
                    provider="openai",
                    model="gpt-3.5-turbo",
                )
            
            response = await service.chat(prompt)
            result = cls._parse_convert_response(
                response.content,
                original_platform,
                request.target_platform.value,
                original_title,
            )
            
            # 保存为新的创作记录
            new_creation = Creation(
                user_id=user_id,
                creation_type=cls.PLATFORM_TO_CREATION_TYPE.get(
                    request.target_platform,
                    CreationType.WECHAT_ARTICLE
                ),
                tool_type=request.target_platform.value,
                title=result.converted_title,
                input_data={
                    "source_creation_id": original.id,
                    "source_platform": original_platform,
                    "target_platform": request.target_platform.value,
                    "style_adjustment": request.style_adjustment,
                },
                output_content=result.converted_content,
                status=CreationStatus.COMPLETED,
                parent_id=original.id,
                source_platform=original_platform,
            )
            db.add(new_creation)
            db.commit()
            db.refresh(new_creation)
            
            result.creation_id = new_creation.id
            return result
            
        except Exception as e:
            logger.error(f"内容转换失败: {e}")
            raise Exception(f"内容转换失败: {str(e)}")
    
    @classmethod
    async def batch_convert(
        cls,
        request: BatchConvertRequest,
        db: Session,
        user_id: int,
        ai_model=None,
    ) -> BatchConvertResult:
        """批量转换到多个平台"""
        results = []
        success_count = 0
        failed_count = 0
        
        for platform in request.target_platforms:
            try:
                convert_request = ConvertRequest(
                    creation_id=request.creation_id,
                    target_platform=platform,
                    style_adjustment=request.style_adjustment,
                )
                result = await cls.convert(convert_request, db, user_id, ai_model)
                results.append(result)
                success_count += 1
            except Exception as e:
                logger.error(f"转换到 {platform} 失败: {e}")
                failed_count += 1
        
        return BatchConvertResult(
            original_creation_id=request.creation_id,
            results=results,
            success_count=success_count,
            failed_count=failed_count,
        )
    
    @classmethod
    def _build_convert_prompt(
        cls,
        original_content: str,
        original_title: str,
        original_platform: str,
        target_platform: TargetPlatform,
        target_info: PlatformInfo,
        style_adjustment: Optional[str],
        keep_structure: bool,
        add_emojis: bool,
        generate_tags: bool,
    ) -> str:
        """构建转换提示词"""
        
        emoji_instruction = "在适当位置添加emoji表情符号，使内容更生动" if add_emojis else "不要添加emoji"
        structure_instruction = "尽量保留原文的核心结构和逻辑" if keep_structure else "可以完全重组内容结构"
        tags_instruction = "生成5-10个适合该平台的话题标签" if generate_tags else ""
        style_instruction = f"风格调整要求：{style_adjustment}" if style_adjustment else ""
        
        return f"""你是一位资深的多平台内容运营专家，擅长将内容转换为不同平台的最佳格式。

## 任务
将以下内容从「{original_platform}」格式转换为「{target_info.name}」格式。

## 原始内容
标题：{original_title}

正文：
{original_content}

## 目标平台特点
- 平台：{target_info.name}
- 字数限制：{target_info.max_length or '无限制'}字以内
- 平台特点：{', '.join(target_info.features)}
- 写作技巧：{', '.join(target_info.tips)}

## 转换要求
1. {structure_instruction}
2. {emoji_instruction}
3. 语言风格要符合{target_info.name}用户的阅读习惯
4. 保留原文的核心信息和观点
5. 字数控制在平台限制内
{style_instruction}

## 输出格式
严格按照以下JSON格式输出：
```json
{{
  "converted_title": "转换后的标题",
  "converted_content": "转换后的正文内容",
  "tags": ["标签1", "标签2"],
  "word_count": 字数,
  "conversion_notes": ["转换说明1", "转换说明2"]
}}
```"""
    
    @classmethod
    def _parse_convert_response(
        cls,
        ai_response: str,
        original_platform: str,
        target_platform: str,
        original_title: str,
    ) -> ConvertResult:
        """解析转换响应"""
        try:
            # 提取 JSON
            json_str = ai_response
            if "```json" in ai_response:
                json_str = ai_response.split("```json")[1].split("```")[0]
            elif "```" in ai_response:
                json_str = ai_response.split("```")[1].split("```")[0]
            
            data = json.loads(json_str.strip())
            
            return ConvertResult(
                original_platform=original_platform,
                target_platform=target_platform,
                original_title=original_title,
                converted_title=data.get("converted_title", original_title),
                converted_content=data.get("converted_content", ""),
                tags=data.get("tags", []),
                word_count=data.get("word_count", 0),
                conversion_notes=data.get("conversion_notes", []),
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"解析转换响应失败: {e}")
            raise Exception("AI 响应解析失败，请重试")
