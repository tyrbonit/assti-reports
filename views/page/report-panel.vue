<template>
    <div>
        <el-radio-group v-model="reporttype" size="mini">
          <el-radio-button
           v-for="item in reporttypes"
          :key="item.value"
          :label="item.value">
              <span v-text="item.label"></span>
          </el-radio-button>
        </el-radio-group>
        <el-date-picker
          v-model="datarange"
          type="datetimerange"
          align="right"
          start-placeholder="Start Date"
          end-placeholder="End Date"
          :default-time="['08:00:00', '08:00:00']"
          value-format="dd.MM.yyyy HH:mm:ss"
          time-arrow-control
                        size="mini">
        </el-date-picker>
    </div>
</template>
<script>
    module.exports = {
        name: 'report-panel',
        props: {
            oneperiod: {
                type: Boolean,
                default: false
            },
            /*rtypes: {
                type: String,
                default: ";"
            },*/
        },
        data: function () {
            return {
                datarange: "",
                reporttype: "",
                rtypes: ";"
            }
        },
        computed: {
            reporttypes: function(){
                var labels = {"getMirror":"тек.",
                              "smene":"смена",
                              "43200":"сут.",
                              "86400":"12ч",
                              "3600":"час",
                              "1800":"30м",
                              "900":"15м",
                              "60":"мин",
                              "10":"10с",
                             };
                return this.rtypes.split(";").slice(0, -1).map(
                    function (value) {
                        return {value: value, label: labels[value]}
                    });
            },
            
        },
        watch: {
            '$route': function (to, from) {
                console.log(to);
                this.rtypes = to.params.rtypes
                if (this.reporttypes.length) this.reporttype = this.reporttypes[0].value;
            },
            datarange: function(a, b){console.log(a)}
        },
    }
</script>
<style></style>
