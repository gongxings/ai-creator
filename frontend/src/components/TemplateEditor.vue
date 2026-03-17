<template>
  <div class="template-editor">
    <div class="editor-layout">
      <!-- 左侧：样式编辑面板 -->
      <div class="editor-panel">
        <div class="panel-header">
          <el-input
            v-model="templateData.name"
            placeholder="模板名称"
            size="large"
            class="template-name-input"
          />
          <el-input
            v-model="templateData.description"
            placeholder="模板描述（可选）"
            size="small"
            class="template-desc-input"
          />
        </div>

        <el-tabs v-model="activeTab" class="style-tabs">
          <!-- 容器样式 -->
          <el-tab-pane label="容器" name="container">
            <StyleSection title="容器样式">
              <ColorPicker v-model="styles.container.backgroundColor" label="背景颜色" />
              <InputField v-model="styles.container.padding" label="内边距" placeholder="如: 20px" />
              <InputField v-model="styles.container.maxWidth" label="最大宽度" placeholder="如: 800px" />
              <InputField v-model="styles.container.fontFamily" label="字体" placeholder="如: 'PingFang SC', sans-serif" />
            </StyleSection>
          </el-tab-pane>

          <!-- 标题样式 -->
          <el-tab-pane label="标题" name="headings">
            <StyleSection title="一级标题 (H1)">
              <ColorPicker v-model="styles.h1.color" label="颜色" />
              <InputField v-model="styles.h1.fontSize" label="字号" placeholder="如: 24px" />
              <SelectField v-model="styles.h1.fontWeight" label="字重" :options="fontWeightOptions" />
              <InputField v-model="styles.h1.marginBottom" label="下边距" placeholder="如: 16px" />
              <InputField v-model="styles.h1.borderBottom" label="底部边框" placeholder="如: 2px solid #333" />
              <InputField v-model="styles.h1.paddingBottom" label="底部内边距" placeholder="如: 8px" />
            </StyleSection>

            <StyleSection title="二级标题 (H2)">
              <ColorPicker v-model="styles.h2.color" label="颜色" />
              <InputField v-model="styles.h2.fontSize" label="字号" placeholder="如: 20px" />
              <SelectField v-model="styles.h2.fontWeight" label="字重" :options="fontWeightOptions" />
              <InputField v-model="styles.h2.marginTop" label="上边距" placeholder="如: 24px" />
              <InputField v-model="styles.h2.marginBottom" label="下边距" placeholder="如: 12px" />
              <InputField v-model="styles.h2.borderLeft" label="左侧边框" placeholder="如: 4px solid #409eff" />
              <InputField v-model="styles.h2.paddingLeft" label="左侧内边距" placeholder="如: 12px" />
            </StyleSection>

            <StyleSection title="三级标题 (H3)">
              <ColorPicker v-model="styles.h3.color" label="颜色" />
              <InputField v-model="styles.h3.fontSize" label="字号" placeholder="如: 18px" />
              <SelectField v-model="styles.h3.fontWeight" label="字重" :options="fontWeightOptions" />
              <InputField v-model="styles.h3.marginTop" label="上边距" placeholder="如: 20px" />
              <InputField v-model="styles.h3.marginBottom" label="下边距" placeholder="如: 10px" />
            </StyleSection>
          </el-tab-pane>

          <!-- 段落样式 -->
          <el-tab-pane label="段落" name="paragraph">
            <StyleSection title="段落 (P)">
              <ColorPicker v-model="styles.p.color" label="颜色" />
              <InputField v-model="styles.p.fontSize" label="字号" placeholder="如: 16px" />
              <InputField v-model="styles.p.lineHeight" label="行高" placeholder="如: 1.8" />
              <InputField v-model="styles.p.marginBottom" label="下边距" placeholder="如: 12px" />
              <InputField v-model="styles.p.textIndent" label="首行缩进" placeholder="如: 2em" />
              <SelectField v-model="styles.p.textAlign" label="对齐" :options="textAlignOptions" />
            </StyleSection>

            <StyleSection title="强调文字">
              <div class="sub-section">
                <span class="sub-title">加粗 (strong)</span>
                <ColorPicker v-model="styles.strong.color" label="颜色" />
                <SelectField v-model="styles.strong.fontWeight" label="字重" :options="fontWeightOptions" />
              </div>
              <div class="sub-section">
                <span class="sub-title">斜体 (em)</span>
                <ColorPicker v-model="styles.em.color" label="颜色" />
                <SelectField v-model="styles.em.fontStyle" label="样式" :options="fontStyleOptions" />
              </div>
            </StyleSection>
          </el-tab-pane>

          <!-- 引用样式 -->
          <el-tab-pane label="引用" name="blockquote">
            <StyleSection title="引用块 (blockquote)">
              <ColorPicker v-model="styles.blockquote.color" label="文字颜色" />
              <ColorPicker v-model="styles.blockquote.backgroundColor" label="背景颜色" />
              <InputField v-model="styles.blockquote.fontSize" label="字号" placeholder="如: 15px" />
              <InputField v-model="styles.blockquote.padding" label="内边距" placeholder="如: 12px 16px" />
              <InputField v-model="styles.blockquote.marginTop" label="上边距" placeholder="如: 16px" />
              <InputField v-model="styles.blockquote.marginBottom" label="下边距" placeholder="如: 16px" />
              <InputField v-model="styles.blockquote.borderLeft" label="左侧边框" placeholder="如: 4px solid #409eff" />
              <InputField v-model="styles.blockquote.borderRadius" label="圆角" placeholder="如: 4px" />
            </StyleSection>
          </el-tab-pane>

          <!-- 列表样式 -->
          <el-tab-pane label="列表" name="list">
            <StyleSection title="无序列表 (ul)">
              <InputField v-model="styles.ul.marginTop" label="上边距" placeholder="如: 12px" />
              <InputField v-model="styles.ul.marginBottom" label="下边距" placeholder="如: 12px" />
              <InputField v-model="styles.ul.paddingLeft" label="左侧内边距" placeholder="如: 24px" />
            </StyleSection>

            <StyleSection title="有序列表 (ol)">
              <InputField v-model="styles.ol.marginTop" label="上边距" placeholder="如: 12px" />
              <InputField v-model="styles.ol.marginBottom" label="下边距" placeholder="如: 12px" />
              <InputField v-model="styles.ol.paddingLeft" label="左侧内边距" placeholder="如: 24px" />
            </StyleSection>

            <StyleSection title="列表项 (li)">
              <ColorPicker v-model="styles.li.color" label="颜色" />
              <InputField v-model="styles.li.fontSize" label="字号" placeholder="如: 15px" />
              <InputField v-model="styles.li.lineHeight" label="行高" placeholder="如: 1.8" />
              <InputField v-model="styles.li.marginBottom" label="下边距" placeholder="如: 6px" />
            </StyleSection>
          </el-tab-pane>

          <!-- 代码样式 -->
          <el-tab-pane label="代码" name="code">
            <StyleSection title="行内代码 (code)">
              <ColorPicker v-model="styles.code.color" label="文字颜色" />
              <ColorPicker v-model="styles.code.backgroundColor" label="背景颜色" />
              <InputField v-model="styles.code.fontSize" label="字号" placeholder="如: 14px" />
              <InputField v-model="styles.code.padding" label="内边距" placeholder="如: 2px 6px" />
              <InputField v-model="styles.code.borderRadius" label="圆角" placeholder="如: 4px" />
              <InputField v-model="styles.code.fontFamily" label="字体" placeholder="如: 'Consolas', monospace" />
            </StyleSection>

            <StyleSection title="代码块 (pre)">
              <ColorPicker v-model="styles.pre.color" label="文字颜色" />
              <ColorPicker v-model="styles.pre.backgroundColor" label="背景颜色" />
              <InputField v-model="styles.pre.padding" label="内边距" placeholder="如: 16px" />
              <InputField v-model="styles.pre.borderRadius" label="圆角" placeholder="如: 8px" />
              <InputField v-model="styles.pre.fontSize" label="字号" placeholder="如: 14px" />
              <InputField v-model="styles.pre.lineHeight" label="行高" placeholder="如: 1.6" />
            </StyleSection>
          </el-tab-pane>

          <!-- 其他样式 -->
          <el-tab-pane label="其他" name="other">
            <StyleSection title="链接 (a)">
              <ColorPicker v-model="styles.a.color" label="颜色" />
              <SelectField v-model="styles.a.textDecoration" label="下划线" :options="textDecorationOptions" />
            </StyleSection>

            <StyleSection title="图片 (img)">
              <InputField v-model="styles.img.maxWidth" label="最大宽度" placeholder="如: 100%" />
              <InputField v-model="styles.img.borderRadius" label="圆角" placeholder="如: 8px" />
              <InputField v-model="styles.img.marginTop" label="上边距" placeholder="如: 16px" />
              <InputField v-model="styles.img.marginBottom" label="下边距" placeholder="如: 16px" />
              <InputField v-model="styles.img.boxShadow" label="阴影" placeholder="如: 0 2px 8px rgba(0,0,0,0.1)" />
            </StyleSection>

            <StyleSection title="分隔线 (hr)">
              <InputField v-model="styles.hr.borderTop" label="边框样式" placeholder="如: 1px solid #e4e7ed" />
              <InputField v-model="styles.hr.marginTop" label="上边距" placeholder="如: 24px" />
              <InputField v-model="styles.hr.marginBottom" label="下边距" placeholder="如: 24px" />
            </StyleSection>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 右侧：实时预览 -->
      <div class="preview-panel">
        <div class="panel-header">
          <span class="title">实时预览</span>
          <el-switch
            v-model="showPhonePreview"
            active-text="手机"
            inactive-text="页面"
            size="small"
          />
        </div>
        <div class="preview-wrapper">
          <ContentPreview
            :content="sampleMarkdown"
            :template="previewTemplate"
            :is-markdown="true"
            :show-copy-button="false"
            article-title="示例文章"
          />
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="editor-footer">
      <div class="footer-left">
        <el-checkbox v-model="templateData.is_public">公开模板（其他用户可见）</el-checkbox>
      </div>
      <div class="footer-right">
        <el-button @click="$emit('cancel')">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存修改' : '创建模板' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import ContentPreview from './ContentPreview.vue'
import { sampleMarkdown } from '@/services/markdownRenderer'
import type { ArticleTemplate, TemplateStyles, CSSProperties, TemplateCreate, TemplateUpdate } from '@/types/template'
import { createTemplate, updateTemplate } from '@/api/templates'

// 子组件：颜色选择器
const ColorPicker = {
  props: ['modelValue', 'label'],
  emits: ['update:modelValue'],
  template: `
    <div class="style-field">
      <label>{{ label }}</label>
      <el-color-picker 
        :model-value="modelValue" 
        @update:model-value="$emit('update:modelValue', $event)"
        show-alpha
        size="small"
      />
    </div>
  `
}

// 子组件：输入框
const InputField = {
  props: ['modelValue', 'label', 'placeholder'],
  emits: ['update:modelValue'],
  template: `
    <div class="style-field">
      <label>{{ label }}</label>
      <el-input 
        :model-value="modelValue" 
        @update:model-value="$emit('update:modelValue', $event)"
        :placeholder="placeholder"
        size="small"
        clearable
      />
    </div>
  `
}

// 子组件：下拉选择
const SelectField = {
  props: ['modelValue', 'label', 'options'],
  emits: ['update:modelValue'],
  template: `
    <div class="style-field">
      <label>{{ label }}</label>
      <el-select 
        :model-value="modelValue" 
        @update:model-value="$emit('update:modelValue', $event)"
        size="small"
        clearable
        placeholder="请选择"
      >
        <el-option 
          v-for="opt in options" 
          :key="opt.value" 
          :label="opt.label" 
          :value="opt.value" 
        />
      </el-select>
    </div>
  `
}

// 子组件：样式分组
const StyleSection = {
  props: ['title'],
  template: `
    <div class="style-section">
      <div class="section-title">{{ title }}</div>
      <div class="section-content">
        <slot></slot>
      </div>
    </div>
  `
}

const props = defineProps<{
  template?: ArticleTemplate | null
}>()

const emit = defineEmits<{
  (e: 'save', template: ArticleTemplate): void
  (e: 'cancel'): void
}>()

const isEdit = computed(() => !!props.template?.id)

// 模板基本信息
const templateData = reactive({
  name: '',
  description: '',
  is_public: false
})

// 默认样式结构
const createDefaultStyles = (): Record<keyof TemplateStyles, CSSProperties> => ({
  container: {},
  h1: {},
  h2: {},
  h3: {},
  p: {},
  blockquote: {},
  ul: {},
  ol: {},
  li: {},
  code: {},
  pre: {},
  img: {},
  a: {},
  hr: {},
  strong: {},
  em: {}
})

// 样式数据
const styles = reactive<Record<keyof TemplateStyles, CSSProperties>>(createDefaultStyles())

const activeTab = ref('container')
const showPhonePreview = ref(false)
const saving = ref(false)

// 选项配置
const fontWeightOptions = [
  { label: '正常', value: 'normal' },
  { label: '中等', value: '500' },
  { label: '粗体', value: '600' },
  { label: '加粗', value: 'bold' },
  { label: '特粗', value: '700' }
]

const textAlignOptions = [
  { label: '左对齐', value: 'left' },
  { label: '居中', value: 'center' },
  { label: '右对齐', value: 'right' },
  { label: '两端对齐', value: 'justify' }
]

const fontStyleOptions = [
  { label: '正常', value: 'normal' },
  { label: '斜体', value: 'italic' }
]

const textDecorationOptions = [
  { label: '无', value: 'none' },
  { label: '下划线', value: 'underline' }
]

// 预览用的模板对象
const previewTemplate = computed<ArticleTemplate>(() => ({
  id: props.template?.id || 0,
  name: templateData.name || '新模板',
  description: templateData.description,
  styles: cleanStyles(styles),
  is_system: false,
  is_public: templateData.is_public,
  use_count: 0,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
}))

// 清理空值
const cleanStyles = (rawStyles: Record<string, CSSProperties>): TemplateStyles => {
  const result: TemplateStyles = {}
  
  for (const [key, props] of Object.entries(rawStyles)) {
    const cleanedProps: CSSProperties = {}
    let hasValue = false
    
    for (const [propKey, propValue] of Object.entries(props)) {
      if (propValue !== undefined && propValue !== null && propValue !== '') {
        cleanedProps[propKey] = propValue
        hasValue = true
      }
    }
    
    if (hasValue) {
      result[key] = cleanedProps
    }
  }
  
  return result
}

// 初始化模板数据
const initFromTemplate = (template: ArticleTemplate | null | undefined) => {
  if (template) {
    templateData.name = template.name
    templateData.description = template.description || ''
    templateData.is_public = template.is_public
    
    // 重置样式
    const defaultStyles = createDefaultStyles()
    for (const key of Object.keys(defaultStyles) as (keyof TemplateStyles)[]) {
      styles[key] = { ...defaultStyles[key], ...(template.styles[key] || {}) }
    }
  } else {
    templateData.name = ''
    templateData.description = ''
    templateData.is_public = false
    
    const defaultStyles = createDefaultStyles()
    for (const key of Object.keys(defaultStyles) as (keyof TemplateStyles)[]) {
      styles[key] = { ...defaultStyles[key] }
    }
  }
}

// 保存模板
const handleSave = async () => {
  if (!templateData.name.trim()) {
    ElMessage.warning('请输入模板名称')
    return
  }

  saving.value = true
  
  try {
    const cleanedStyles = cleanStyles(styles)
    
    if (isEdit.value && props.template) {
      // 更新模板
      const updateData: TemplateUpdate = {
        name: templateData.name,
        description: templateData.description || undefined,
        styles: cleanedStyles,
        is_public: templateData.is_public
      }
      
      const result = await updateTemplate(props.template.id, updateData)
      ElMessage.success('模板已更新')
      emit('save', result)
    } else {
      // 创建模板
      const createData: TemplateCreate = {
        name: templateData.name,
        description: templateData.description || undefined,
        styles: cleanedStyles,
        is_public: templateData.is_public
      }
      
      const result = await createTemplate(createData)
      ElMessage.success('模板已创建')
      emit('save', result)
    }
  } catch (error: any) {
    console.error('保存模板失败:', error)
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 监听模板变化
watch(() => props.template, (newTemplate) => {
  initFromTemplate(newTemplate)
}, { immediate: true })

// 暴露方法
defineExpose({
  getTemplateData: () => ({
    ...templateData,
    styles: cleanStyles(styles)
  })
})
</script>

<style scoped lang="scss">
.template-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f5f7fa;

  .editor-layout {
    display: flex;
    flex: 1;
    overflow: hidden;
    gap: 16px;
    padding: 16px;

    // 左侧编辑面板
    .editor-panel {
      width: 400px;
      background: #fff;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      overflow: hidden;

      .panel-header {
        padding: 16px;
        border-bottom: 1px solid #e4e7ed;

        .template-name-input {
          margin-bottom: 8px;

          :deep(.el-input__inner) {
            font-size: 18px;
            font-weight: 500;
          }
        }
      }

      .style-tabs {
        flex: 1;
        overflow: hidden;
        display: flex;
        flex-direction: column;

        :deep(.el-tabs__header) {
          padding: 0 16px;
          margin-bottom: 0;
        }

        :deep(.el-tabs__content) {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
        }
      }
    }

    // 右侧预览面板
    .preview-panel {
      flex: 1;
      background: #fff;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      overflow: hidden;

      .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid #e4e7ed;

        .title {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
        }
      }

      .preview-wrapper {
        flex: 1;
        overflow: hidden;

        :deep(.content-preview) {
          height: 100%;

          .preview-toolbar {
            display: none;
          }

          .page-preview,
          .phone-preview {
            height: 100%;
          }
        }
      }
    }
  }

  // 底部操作栏
  .editor-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: #fff;
    border-top: 1px solid #e4e7ed;

    .footer-right {
      display: flex;
      gap: 8px;
    }
  }
}

// 样式分组
.style-section {
  margin-bottom: 20px;

  &:last-child {
    margin-bottom: 0;
  }

  .section-title {
    font-size: 14px;
    font-weight: 500;
    color: #303133;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #ebeef5;
  }

  .section-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .sub-section {
    background: #f5f7fa;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 8px;

    .sub-title {
      display: block;
      font-size: 13px;
      color: #606266;
      margin-bottom: 8px;
    }
  }
}

// 样式字段
.style-field {
  display: flex;
  align-items: center;
  gap: 8px;

  label {
    width: 80px;
    font-size: 13px;
    color: #606266;
    flex-shrink: 0;
  }

  .el-input,
  .el-select {
    flex: 1;
  }

  .el-color-picker {
    width: auto;
  }
}
</style>
