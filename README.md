<div class="project-intro" style="font-family: Arial, sans-serif; max-width: 800px; margin: auto; line-height: 1.6;">
  <h2 style="text-align: center; color: #2c3e50;">Giới thiệu dự án TruyenFileSHA-256</h2>
  
  <p>
    <strong>TruyenFileSHA-256</strong> là một ứng dụng web được phát triển bằng <em>Flask</em> kết hợp với <em>Flask-SocketIO</em>, cung cấp giải pháp truyền file trực tiếp giữa các người dùng thông qua mạng nội bộ hoặc Internet.
    Ứng dụng sử dụng <strong>đăng nhập bảo mật với Flask-Login và mã hóa mật khẩu bằng bcrypt</strong> để quản lý người dùng và phiên làm việc an toàn.
  </p>

  <p>Những chức năng nổi bật của ứng dụng:</p>
  <ul>
    <li><strong>Đăng nhập và xác thực người dùng:</strong> Hệ thống quản lý đăng nhập với bảo mật cao, giúp phân biệt và kiểm soát truy cập người dùng.</li>
    <li><strong>Tạo phòng chat truyền file:</strong> Người dùng có thể bắt đầu các phòng kết nối riêng tư để gửi nhận file an toàn với những người khác.</li>
    <li><strong>Truyền và nhận file qua WebSocket:</strong> File được mã hóa dạng Base64 và gửi qua giao thức WebSocket, giảm thiểu độ trễ và tăng tốc độ truyền tải.</li>
    <li><strong>Lưu trữ file tạm và tính toán mã băm SHA-256:</strong> Mỗi file khi nhận được được lưu tạm trên server, đồng thời tính toán mã băm SHA-256 để đảm bảo tính toàn vẹn dữ liệu.</li>
    <li><strong>Tải file từ server về:</strong> Hỗ trợ người dùng tải file đã được truyền và kiểm tra mã băm để đảm bảo không bị thay đổi, giả mạo.</li>
    <li><strong>Ghi nhận log chi tiết:</strong> Hệ thống ghi lại nhật ký hoạt động như đăng nhập, truyền file, tải file giúp theo dõi và quản lý dễ dàng hơn.</li>
  </ul>

  <div style="display: flex; justify-content: space-around; margin-top: 30px;">
    <div style="flex: 1; margin-right: 10px; text-align: center;">
      <h3>Giao diện đăng nhập</h3>
      <img src="https://github.com/hiepnguyen05/TruyenFileSHA-256/blob/main/dangnhap.png?raw=true" alt="Ảnh màn hình đăng nhập" style="max-width: 100%; border: 1px solid #ccc; border-radius: 8px;">
      <p>Người dùng đăng nhập an toàn với tên tài khoản và mật khẩu được mã hóa.</p>
    </div>
    <div style="flex: 1; margin-left: 10px; text-align: center;">
      <h3>Giao diện truyền file</h3>
      <img src="https://github.com/hiepnguyen05/TruyenFileSHA-256/blob/main/ungdung.png?raw=true" alt="Ảnh giao diện truyền file" style="max-width: 100%; border: 1px solid #ccc; border-radius: 8px;">
      <p>Giao diện cho phép chọn file, truyền file nhanh chóng và kiểm tra mã băm SHA-256 đảm bảo an toàn dữ liệu.</p>
    </div>
  </div>

  <p style="margin-top: 30px;">
    Dự án phù hợp với những ai muốn tìm hiểu về truyền file thời gian thực qua mạng, bảo mật dữ liệu, cũng như ứng dụng WebSocket trong phát triển web hiện đại.
  </p>
</div>
