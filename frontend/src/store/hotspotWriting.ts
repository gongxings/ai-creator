import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface HotspotWriteData {
  topic: string
  keywords: string
  additional_description: string
  tool_type: string
}

export const useHotspotWritingStore = defineStore('hotspotWriting', () => {
  const hotspotData = ref<HotspotWriteData | null>(null)

  const hasPendingData = computed(() => !!hotspotData.value?.topic)

  function setHotspotData(data: HotspotWriteData) {
    hotspotData.value = data
  }

  function clearHotspotData() {
    hotspotData.value = null
  }

  function consumeHotspotData(): HotspotWriteData | null {
    const data = hotspotData.value
    hotspotData.value = null
    return data
  }

  return {
    hotspotData,
    hasPendingData,
    setHotspotData,
    clearHotspotData,
    consumeHotspotData,
  }
})
