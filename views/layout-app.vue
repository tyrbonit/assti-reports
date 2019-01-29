<template>
    <el-container style="height: 100%;">
        <el-header v-if="header">
            <slot name="header"></slot>
        </el-header>
        <el-container>
            <el-aside v-if="aside" width="100" :style="{'overflow-y': 'hidden'}">
                <slot name="aside"></slot>
            </el-aside>
            <el-main>
                <slot></slot>
            </el-main>
            <el-footer v-if="footer"><slot name="footer"></slot></el-footer>
        </el-container>
    </el-container>
</template>
<style>
    html, body, #layout-app {margin: 0;height: 100%;}
</style>

<script>
  module.exports= {
      name: 'layout-app',
      props: {
          aside: {type: Boolean, default: false},
          header: {type: Boolean, default: false},
          footer: {type: Boolean, default: false}
             }
  };
</script>
