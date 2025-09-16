import { defineStore } from 'pinia'

export const useTemplateStore = defineStore('template', {
  state: () => ({
    userMessage: '' as string
  }),
  actions: {
    setUserMessage(text: string) {
      this.userMessage = text
    },
    clearUserMessage() {
      this.userMessage = ''
    }
  }
})
