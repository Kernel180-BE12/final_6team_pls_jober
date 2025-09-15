import { defineStore } from 'pinia'

export const useTemplateStore = defineStore('template', {
  state: () => ({
    userText: '' as string
  }),
  actions: {
    setUserText(text: string) {
      this.userText = text
    },
    clearUserText() {
      this.userText = ''
    }
  }
})
