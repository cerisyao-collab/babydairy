Page({
  data: {
    showHeightWeightModal: false,
    showTemperatureModal: false,
    height: '',
    weight: '',
    head: '',
    foot: '',
    temperature: 36.5
  },

  // 通用输入绑定
  onInputChange(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({ [field]: e.detail.value });
  },

  // slider 绑定
  onTemperatureSliderChange(e) {
    this.setData({ temperature: e.detail.value });
  },

  noop() {},
  closeModalByMask() {},

  // 打开/关闭弹窗
  openHeightWeightModal() {
    this.setData({ showHeightWeightModal: true });
  },
  closeHeightWeightModal() {
    this.setData({ showHeightWeightModal: false });
  },
  openTemperatureModal() {
    this.setData({ showTemperatureModal: true });
  },
  closeTemperatureModal() {
    this.setData({ showTemperatureModal: false });
  },

  // ================== 生长指标 ==================
  async recordHeightWeight() {
    const api = require('../../utils/api');
    const { height, weight, head, foot } = this.data;

    const fields = [
      { key: 'height_cm', value: height },
      { key: 'weight_kg', value: weight },
      { key: 'head_cm', value: head },
      { key: 'foot_cm', value: foot }
    ];

    try {
      wx.showLoading({ title: '记录中...' });

      const details = {};
      for (const f of fields) {
        const val = parseFloat(f.value);
        if (f.value && !isNaN(val)) {
          details[f.key] = val;
        }
      }

      if (Object.keys(details).length === 0) {
        wx.hideLoading();
        wx.showToast({ title: '请填写有效数据', icon: 'none' });
        return;
      }

      await api.createRecord('growth', details);

      wx.hideLoading();
      wx.showToast({ title: '生长指标记录成功', icon: 'success' });

      this.closeHeightWeightModal();
      this.setData({ height: '', weight: '', head: '', foot: '' });

    } catch (err) {
      wx.hideLoading();
      console.error('记录失败', err);
      wx.showToast({ title: err.message || '记录失败', icon: 'none' });
    }
  },

  // ================== 体温 ==================
  async recordTemperature() {
    const api = require('../../utils/api');
    const { temperature } = this.data;
    const val = parseFloat(temperature);

    if (!temperature || isNaN(val)) {
      wx.showToast({ title: '请输入正确体温', icon: 'none' });
      return;
    }

    try {
      wx.showLoading({ title: '记录中...' });

      await api.createRecord('illness', {
        temperature: val,
        symptom: '体温记录'
      });

      wx.hideLoading();
      wx.showToast({ title: '体温记录成功', icon: 'success' });

      this.closeTemperatureModal();
      this.setData({ temperature: 36.5 });

    } catch (err) {
      wx.hideLoading();
      console.error('记录失败', err);
      wx.showToast({ title: err.message || '记录失败', icon: 'none' });
    }
  },

  // ================== 其他护理 ==================
  async recordBathing() {
    const api = require('../../utils/api');
    try {
      await api.createRecord('bathing', {});
      wx.showToast({ title: '洗澡记录成功', icon: 'success' });
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '失败', icon: 'none' });
    }
  }
});
