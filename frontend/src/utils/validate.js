/**
 * 全系统通用的表单校验规则库
 */

// 1. 校验手机号
export function validatePhone(rule, value, callback) {
  // 如果非必填且为空，直接通过
  if (!value) {
    callback()
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    // 强制只能是以1开头、第二位3-9、总长11位的纯数字
    callback(new Error('请输入正确的11位手机号码，且不能包含非法字符'))
  } else {
    callback()
  }
}

// 2. 校验邮箱
export function validateEmail(rule, value, callback) {
  if (!value) {
    callback()
  } else if (!/^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/.test(value)) {
    callback(new Error('请输入正确的邮箱格式'))
  } else {
    callback()
  }
}

// 3. 中国省份/直辖市标准数据字典 (供下拉框使用)
export const provinceList = [
  '北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
  '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南',
  '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州',
  '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '台湾', '香港', '澳门'
]