nreal_protocol = Proto("Nreal_Air",  "Nreal Air Protocol")


local mgs_ids = {
	[0x0008] = "W_DISP_MODE",
  [0x0015] = "R_GLASSID",
  [0x0016] = "R_DP7911_FW_VERSION",
  [0x0018] = "R_DSP_VERSION",
  [0x0019] = "W_CANCEL_ACTIVATION",
  [0x0021] = "R_DSP_APP_FW_VERSION",
  [0x0026] = "R_MCU_APP_FW_VERSION",
  [0x0029] = "R_ACTIVATION_TIME",
  [0x002A] = "W_ACTIVATION_TIME",
  [0x0026] = "R_MCU_APP_FW_VERSION",
  [0x0026] = "R_MCU_APP_FW_VERSION",
  [0x0026] = "R_MCU_APP_FW_VERSION",
  [0x0026] = "R_MCU_APP_FW_VERSION",
  [0x6C05] = "P_BUTTON_PRESSED",
	[0x6c09] = "ASYNC_TEXT_LOG",
  [0x6c02] = "P_UKNOWN_HEARTBEAT",
  [0x6c12] = "P_UKNOWN_HEARTBEAT_2"
}

local f_encap_type = Field.new("frame.encap_type")

local dar_transfer_type = Field.new("usb.darwin.endpoint_type")
local dar_endpoint = Field.new("usb.darwin.endpoint_address")

local win_transfer_type = Field.new("usb.transfer_type")
local win_endpoint = Field.new("usb.endpoint_address")

header1 = ProtoField.uint8("nreal.header1", "header1", base.HEX)
header2 = ProtoField.uint8("nreal.header2", "header2", base.HEX)

gyro_a = ProtoField.int24("nreal.gyro_a", "gyro_a", base.DEC)
gyro_b = ProtoField.int24("nreal.gyro_b", "gyro_b", base.DEC)
gyro_c = ProtoField.int24("nreal.gyro_c", "gyro_c", base.DEC)

accel_a = ProtoField.int24("nreal.accel_a", "accel_a", base.DEC)
accel_b = ProtoField.int24("nreal.accel_b", "accel_b", base.DEC)
accel_c = ProtoField.int24("nreal.accel_c", "accel_c", base.DEC)

timestamp_ns = ProtoField.uint64("nreal.timestamp_ns", "timestamp_ns", base.DEC)

crc32 = ProtoField.uint32("nreal.crc32", "crc32", base.HEX)
timestamp = ProtoField.uint64("nreal.timestamp", "timestamp", base.DEC)
packet_len = ProtoField.uint16("nreal.packet_len", "packet_len", base.DEC)
reserved = ProtoField.bytes("nreal.reserved", "reserved")
payload = ProtoField.bytes("nreal.payload", "payload")
msg_id = ProtoField.uint16("nreal.msg_id", "msg_id", base.HEX, mgs_ids)



nreal_protocol.fields = { header1, header2, gyro_a, gyro_b, gyro_c, accel_a, accel_b, accel_c, timestamp_ns, crc32, timestamp, packet_len, reserved, payload, msg_id}

function nreal_protocol.dissector(buffer, pinfo, tree)
  local encap_type = tonumber(tostring(f_encap_type()))
  local transfer_type, endpoint, interrupt_transfer_type
  
  if (encap_type == 182) then
    transfer_type = tonumber(tostring(dar_transfer_type()))
    endpoint = tonumber(tostring(dar_endpoint()))
    interrupt_transfer_type = 3
  elseif(encap_type == 152) then
    transfer_type = tonumber(tostring(win_transfer_type()))
    endpoint = tonumber(tostring(win_endpoint()))
    interrupt_transfer_type = 1
  else
    transfer_type = tonumber(tostring(win_transfer_type()))
    endpoint = tonumber(tostring(win_endpoint()))
    interrupt_transfer_type = 1
  end

 if transfer_type == interrupt_transfer_type then
    if (endpoint == 0x84)
    then               
        length = buffer:len()
        if length == 0 then return end

        pinfo.cols.protocol = nreal_protocol.name
        local subtree = tree:add(nreal_protocol, buffer(), "Nreal Air Protocol Data")

        if ((buffer(0,1):le_uint() == 0x01) and (buffer(1,1):le_uint() == 0x02))
        then

          subtree:add_le(timestamp_ns, buffer(5,8))
          
          subtree:add_le(gyro_a,    buffer(18,3))
          subtree:add_le(gyro_b,    buffer(21,3))
          subtree:add_le(gyro_c,    buffer(24,3))

          subtree:add_le(accel_a,    buffer(33,3))
          subtree:add_le(accel_b,    buffer(36,3))
          subtree:add_le(accel_c,    buffer(39,3))

        end

    elseif (endpoint == 0x86 or endpoint == 0x07)
    then
      length = buffer:len()
      if length == 0 then return end

      pinfo.cols.protocol = nreal_protocol.name
      local subtree = tree:add(nreal_protocol, buffer(), "Nreal Air Protocol Data")

      if (buffer(0,1):le_uint() == 0xfd)
      then
        subtree:add_le(crc32, buffer(1,4))
        subtree:add_le(packet_len, buffer(5,2))
        local l_payload_len = buffer(5,2):le_uint() - 17
        subtree:add_le(timestamp, buffer(7,8))
        subtree:add_le(msg_id, buffer(15,2))
        local l_msg_id = buffer(15,2):le_uint()
        subtree:add_le(reserved, buffer(17,5))
        subtree:add(payload, buffer(22,l_payload_len))

        if(l_msg_id == 0x6c09)
        then
          pinfo.cols.info = buffer(22,l_payload_len):string()
        elseif ((l_msg_id == 0x0015 or l_msg_id == 0x0026 or l_msg_id == 0x0021 or l_msg_id == 0x0016 or l_msg_id == 0x0018) and l_payload_len > 0)
        then
          pinfo.cols.info = buffer(23,l_payload_len-1):string()
        end
        
      end

    end
  end

  return 0  
end

local usb_product_dissectors = DissectorTable.get("usb.product")
usb_product_dissectors:add(0x33180424, nreal_protocol)

DissectorTable.get("usb.interrupt"):add(0xffff, nreal_protocol)
DissectorTable.get("usb.interrupt"):add(0xff, nreal_protocol)
DissectorTable.get("usb.protocol"):add(0xff, nreal_protocol)
DissectorTable.get("usb.interrupt"):add(0x03, nreal_protocol)