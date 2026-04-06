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

  // ================== 身高体重 ==================
  async recordHeightWeight() {
    const { height, weight, head, foot } = this.data;
    const { supabase } = require('../../utils/supabase');

    // 获取统一 userId
    let userId = wx.getStorageSync('userId');
    if (!userId) {
      const systemInfo = wx.getSystemInfoSync();
      userId = 'anon_' + systemInfo.brand + '_' + systemInfo.model.replace(/\s/g, '');
    }
    const userName = wx.getStorageSync('userInfo')?.nickName || '匿名用户';

    const fields = [
      { type: 'height', value: height },
      { type: 'weight', value: weight },
      { type: 'head', value: head },
      { type: 'foot', value: foot }
    ];

    try {
      wx.showLoading({ title: '记录中...' });

      const records = [];

      for (const f of fields) {
        const val = parseFloat(f.value);

        // 过滤空值 & NaN
        if (!f.value || isNaN(val)) {
          continue;
        }

        records.push({
          type: f.type,
          value: val,
          user_id: userId,
          user_name: userName
        });
      }

      // 防止全部为空
      if (records.length === 0) {
        wx.hideLoading();
        wx.showToast({
          title: '请填写有效数据',
          icon: 'none'
        });
        return;
      }

      // 一次性插入
      await supabase.insert('records', records);

      wx.hideLoading();
      wx.showToast({ title: '记录成功', icon: 'success' });

      this.closeHeightWeightModal();

      // 清空输入
      this.setData({
        height: '',
        weight: '',
        head: '',
        foot: ''
      });

    } catch (err) {
      wx.hideLoading();
      console.error('插入失败', err);
      wx.showToast({
        title: err.message || '记录失败',
        icon: 'none'
      });
    }
  },

  // ================== 体温 ==================
  async recordTemperature() {
    const { temperature } = this.data;
    const { supabase } = require('../../utils/supabase');

    // 获取统一 userId
    let userId = wx.getStorageSync('userId');
    if (!userId) {
      const systemInfo = wx.getSystemInfoSync();
      userId = 'anon_' + systemInfo.brand + '_' + systemInfo.model.replace(/\s/g, '');
    }
    const userName = wx.getStorageSync('userInfo')?.nickName || '匿名用户';

    const val = parseFloat(temperature);

    if (!temperature || isNaN(val)) {
      wx.showToast({
        title: '请输入正确体温',
        icon: 'none'
      });
      return;
    }

    try {
      wx.showLoading({ title: '记录中...' });

      await supabase.insert('records', {
        type: 'temperature',
        value: val,
        user_id: userId,
        user_name: userName
      });

      wx.hideLoading();
      wx.showToast({ title: '记录成功', icon: 'success' });

      this.closeTemperatureModal();
      this.setData({ temperature: 36.5 });

    } catch (err) {
      wx.hideLoading();
      console.error('插入失败', err);
      wx.showToast({
        title: err.message || '记录失败',
        icon: 'none'
      });
    }
  },

  // ================== 其他护理 ==================
  async recordBathing() {
    const { supabase } = require('../../utils/supabase');
    
    // 获取统一 userId
    let userId = wx.getStorageSync('userId');
    if (!userId) {
      const systemInfo = wx.getSystemInfoSync();
      userId = 'anon_' + systemInfo.brand + '_' + systemInfo.model.replace(/\s/g, '');
    }
    const userName = wx.getStorageSync('userInfo')?.nickName || '匿名用户';
    
    try {
      await supabase.insert('records', {
        type: 'bathing',
        value: null,
        user_id: userId,
        user_name: userName
      });
      wx.showToast({ title: '洗澡记录成功', icon: 'success' });
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '失败', icon: 'none' });
    }
  },

  async recordNailCutting() {
    const { supabase } = require('../../utils/supabase');
    
    // 获取统一 userId
    let userId = wx.getStorageSync('userId');
    if (!userId) {
      const systemInfo = wx.getSystemInfoSync();
      userId = 'anon_' + systemInfo.brand + '_' + systemInfo.model.replace(/\s/g, '');
    }
    const userName = wx.getStorageSync('userInfo')?.nickName || '匿名用户';
    
    try {
      await supabase.insert('records', {
        type: 'nail_cutting',
        value: null,
        user_id: userId,
        user_name: userName
      });
      wx.showToast({ title: '剪指甲记录成功', icon: 'success' });
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '失败', icon: 'none' });
    }
  }
});