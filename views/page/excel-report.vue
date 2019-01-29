<template>
    <object classid='CLSID:0002E551-0000-0000-C000-000000000046'
            class="excelobject" v-on:change-report.native="change">
        <!--param v-for="(value, key) in params" :name="key" :value="value"-->
        <!--param name="XMLURL" value="http://127.0.0.1:8000/reports/page/htmlreport"/-->
    </object>
</template>
<script>
module.exports = {
  name: 'excel-report',
  props: {},
      data: function () {
    return {
        page: 'page87.xml',
        baseurl: "{{=URL(a=request.application, c='page', f= 'report', scheme=True, host=True, extension=False)}}"
    }
  },
    mounted: function () {
        var self = this;
        //this.$el.MaxWidth  = document.body.clientWidth;
        self.$el.EnableResize = false;
        self.$el.MaxWidth = "100%";
        self.$el.MaxHeight = "100%";
        self.$el.Width = "100%";
        self.$el.Width = "100%";
        /*window.addEventListener('resize',
                                _.debounce(function(){
            console.log(self.$parent.$el.clientHeight)
            self.$el.MaxWidth = self.$parent.$el.clientWidth
            self.$el.MaxHeight = self.$parent.$el.clientHeight
            console.log(self.$el.MaxHeight)
        },
200), false);*/
        this.$el.DataType="XMLURL"
        this.navigate(this.$route);
        //this.state.name = this.$route.name;
        //this.state.params = this.$route.params;
        //this.state.query = this.$route.query;
        //this.$el.Refresh()
        //this.$el.setProperty("SelectionNamespaces","xmlns:ss='urn:schemas-microsoft-com:office:spreadsheet'");
        //this.$el.XMLData = this.loadxml('http://127.0.0.1:8000/reports/static/reports/page87.xml')
},
    watch: {
    '$route': function (to, from) {
        console.log(to);
        this.navigate(to);
    },
  },

    created: function(){
        this.getmirror = _.debounce(this.getmirror, 5000);
    },

    updated: function () {
  this.$nextTick(function () {
      this.$el.MaxWidth = this.$parent.$el.clientWidth
      this.$el.MaxHeight = this.$parent.$el.clientHeight
    // Код, который будет запущен только после
    // обновления всех представлений
      //console.log("refresh", this.$el.XMLURL);
      //this.$el.XMLURL = this.params.XMLURL
      //this.$el.UpdatePropertyToolbox()
      //this.$el.BeginUndo()
      //this.$el.Refresh()
      //this.$el.EndUndo()
  })
},
    computed:{
        detectIE: function() {
            var ua = window.navigator.userAgent;
            var msie = ua.indexOf('MSIE ');
            if (msie > 0) {
                // IE 10 or older => return version number
                return parseInt(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
            }
            var trident = ua.indexOf('Trident/');
            if (trident > 0) {
                // IE 11 => return version number
                var rv = ua.indexOf('rv:');
                return parseInt(ua.substring(rv + 3, ua.indexOf('.', rv)), 10);
            }

            var edge = ua.indexOf('Edge/');
            if (edge > 0) {
               // Edge (IE 12+) => return version number
               return parseInt(ua.substring(edge + 5, ua.indexOf('.', edge)), 10);
            }
            // other browser
            return false;
        },
    },
    methods:{
        navigate: function(to){
            if (to.params.pid) {
                if (to.query.type ==='getMirror'){
                    this.getmirror(to.params.pid);
                } else {
                    this.getmirror(false);
                };
                this.$el.XMLURL =  this.baseurl + to.fullPath
                //console.log(to, this.detectIE)
            }
        },
        getmirror: function(pid){
            var url = "{{=URL(a=request.application, c='page', f= 'getmirror', scheme=True, host=True, extension=False)}}",
                sheet=this.$el.ActiveSheet;
            //console.log(pid);
            if (pid){
                this.$http.get(url+'/'+pid).then(function(response) {
                    // get body data
                    var data = response.body;
                    for (i=0; i<data.length; i++) {
                         sheet.Rows(data[i][0]).Cells(data[i][1])=data[i][2]
                    };
                }, function(response) {
                    // error callback
                });
                this.getmirror(pid);
            };
        },
        
    }
}
</script>
<style>
    /*.excelobject{background-color:threedface; border:1px solid #cccccc; height:100%; width:100%; top:0;}*/
    .excelobject{height: 100%!important;width: 100%!important;position:relative;}
</style>
