<script setup lang="ts">
// 信号面板 — useSignalStream 已接入; 阶段 5 起显示真实缠论买卖点事件
import { useSignalStream } from "@/composables/useSignalStream";

const { last, connected, connect, disconnect } = useSignalStream();
connect();
</script>

<template>
  <div class="body">
    <div class="status">
      <span :class="['dot', connected ? 'on' : 'off']" />
      {{ connected ? "已连接 /ws/signal" : "未连接" }}
      <button v-if="!connected" @click="connect" class="btn-sm">重连</button>
      <button v-else @click="disconnect" class="btn-sm">断开</button>
    </div>
    <p v-if="last" class="last">最新: {{ JSON.stringify(last) }}</p>
    <p v-else class="placeholder">买卖点事件列表 — 阶段 5 接通真实信号</p>
  </div>
</template>

<style scoped>
.body { padding: 10px 12px; }
.status { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #b0b0b0; margin-bottom: 6px; }
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.dot.on { background: #4caf50; }
.dot.off { background: #666; }
.last { font-size: 11px; color: #888; word-break: break-all; }
.placeholder { color: #777; font-size: 12px; font-style: italic; }
.btn-sm { font-size: 11px; padding: 1px 6px; background: #333; border: 1px solid #555; color: #aaa; cursor: pointer; border-radius: 3px; }
</style>
