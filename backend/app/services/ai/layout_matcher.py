"""
布局匹配服务
根据大纲内容智能匹配模板布局
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class LayoutMatcher:
    """布局匹配器"""
    
    # 布局类型优先级
    LAYOUT_PRIORITY = {
        "title": ["title", "section"],
        "content": ["content", "two_content"],
        "section": ["section", "title"],
        "ending": ["title", "section"],
    }
    
    def match_outline_to_layout(
        self,
        outline: Dict[str, Any],
        layout_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        将大纲内容匹配到模板布局
        
        Args:
            outline: 大纲内容
            layout_metadata: 模板布局元数据
            
        Returns:
            匹配结果列表，每项包含slide_content和matched_layout
        """
        slides = outline.get("slides", [])
        template_slides = layout_metadata.get("slides", [])
        
        if not slides:
            return []
        
        if not template_slides:
            # 没有模板布局，返回原始内容
            return [{"slide_content": s, "matched_layout": None} for s in slides]
        
        matches = []
        
        for idx, slide_content in enumerate(slides):
            slide_type = slide_content.get("slide_type", "content")
            
            # 查找最佳匹配的布局
            best_layout = self._find_best_layout(slide_type, template_slides, idx)
            
            matches.append({
                "slide_content": slide_content,
                "matched_layout": best_layout,
                "slide_index": idx
            })
        
        return matches
    
    def _find_best_layout(
        self,
        slide_type: str,
        template_slides: List[Dict],
        current_index: int
    ) -> Optional[Dict]:
        """
        查找最佳匹配的布局
        
        Args:
            slide_type: 幻灯片类型
            template_slides: 模板幻灯片列表
            current_index: 当前索引
            
        Returns:
            最佳匹配的布局
        """
        # 首先尝试直接匹配
        for slide in template_slides:
            if slide.get("type") == slide_type:
                return slide
        
        # 尝试按优先级匹配
        priority_types = self.LAYOUT_PRIORITY.get(slide_type, ["content"])
        for ptype in priority_types:
            for slide in template_slides:
                if slide.get("type") == ptype:
                    return slide
        
        # 如果都没有匹配，返回对应索引的布局（如果存在）
        if current_index < len(template_slides):
            return template_slides[current_index]
        
        # 返回第一个布局作为默认
        return template_slides[0] if template_slides else None
    
    def generate_filled_outline(
        self,
        matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        根据匹配结果生成填充后的幻灯片内容
        
        Args:
            matches: 匹配结果列表
            
        Returns:
            填充后的幻灯片内容列表
        """
        filled_slides = []
        
        for match in matches:
            slide_content = match["slide_content"]
            layout = match["matched_layout"]
            
            filled_slide = {
                "title": slide_content.get("title", ""),
                "subtitle": slide_content.get("subtitle", ""),
                "bullets": slide_content.get("bullets", []),
                "notes": slide_content.get("notes", ""),
                "layout_index": layout.get("index") if layout else None,
                "layout_type": layout.get("type") if layout else slide_content.get("slide_type", "content")
            }
            
            filled_slides.append(filled_slide)
        
        return filled_slides
    
    def validate_outline(self, outline: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证并规范化大纲
        
        Args:
            outline: 原始大纲
            
        Returns:
            规范化后的大纲
        """
        # 确保有标题
        if "title" not in outline:
            outline["title"] = "未命名演示文稿"
        
        # 确保slides是列表
        if "slides" not in outline:
            outline["slides"] = []
        
        # 规范化每个slide
        for idx, slide in enumerate(outline["slides"]):
            if isinstance(slide, str):
                # 如果slide是字符串，转换为字典
                outline["slides"][idx] = {
                    "slide_type": "content",
                    "title": slide,
                    "bullets": []
                }
            elif isinstance(slide, dict):
                # 确保必要字段存在
                if "title" not in slide:
                    slide["title"] = f"幻灯片 {idx + 1}"
                if "slide_type" not in slide:
                    slide["slide_type"] = "content"
                if "bullets" not in slide:
                    slide["bullets"] = []
        
        # 确保第一页是标题页
        if outline["slides"] and outline["slides"][0].get("slide_type") != "title":
            outline["slides"][0]["slide_type"] = "title"
        
        return outline


# 全局实例
layout_matcher = LayoutMatcher()
