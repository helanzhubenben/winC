# 客户 Excel 导入模板设计

日期：2026-05-19

## 背景

当前系统是 Fishpool 客户池管理系统，后端使用 Django REST Framework，前端使用 Vue 3 + Element Plus。系统已经具备客户 CRUD、客户导出、全量工作簿导出，以及营收数据 Excel/CSV 导入能力。

本次需求是增加“客户导入”能力，并把需要导入的客户字段做成一个 Excel 模板文件放在项目文件夹里，方便用户按模板批量维护客户数据。

## 目标

1. 提供一份客户导入 Excel 模板文件，放在项目仓库的固定目录中。
2. 支持用户在客户列表页上传 Excel 文件批量导入客户。
3. 导入字段与现有“新增客户”表单保持一致。
4. 客户等级不在 Excel 中手工填写，由系统根据 X/Y/Z 评分自动计算。
5. 导入后返回新增、更新、跳过和错误明细，方便用户检查数据质量。

## 不做范围

1. 不导入联系人信息。
2. 不导入营收数据，营收已有独立导入入口。
3. 不支持多 Sheet 复杂工作簿，仅解析第一个工作表。
4. 不做异步任务队列，当前数据量按同步导入处理。
5. 不引入新的 Excel 库，继续使用现有 `openpyxl`。

## 模板文件位置

模板文件建议放在：

```text
docs/templates/customer_import_template.xlsx
```

理由：

1. 这是给业务用户使用的文件，不是 Django 模板，因此不放在 `backend/templates/`。
2. `docs/templates/` 语义清晰，后续如果有 Weekly Report、联系人、营收等模板，也可以集中管理。
3. 后端下载接口可以直接读取该文件返回给浏览器。

## Excel 模板字段

模板第一行是固定表头。字段如下：

| 列名 | 是否必填 | 对应系统字段 | 说明 |
| --- | --- | --- | --- |
| 客户名称 | 是 | `client_name` / `name` | 用于新增或匹配已有客户 |
| 业务模式 | 是 | `business_model` | 仅允许 `Hunting` 或 `Farming` |
| 区域 | 是 | `area` / `region` | 对应客户区域 |
| 城市 | 是 | `city` | 对应客户城市 |
| 地址 | 否 | `address` | 详细地址 |
| X轴描述 | 否 | `description_x` / `score_x_desc` | 客户潜力说明 |
| X轴评分 | 是 | `score_x` | 0-100 数字 |
| Y轴描述 | 否 | `description_y` / `score_y_desc` | 竞争环境说明 |
| Y轴评分 | 是 | `score_y` | 0-100 数字 |
| Z轴描述 | 否 | `key_person` / `score_z_desc` | 关键人关系说明 |
| Z轴评分 | 是 | `score_z` | 0-100 数字 |
| 客户策略 | 否 | `client_strategy` / `strategy` | 客户策略 |
| 潜在贡献 | 否 | `potential_contribution` | 数字，单位沿用系统现有定义 |
| 备注 | 否 | `remark` / `notes` | 备注信息 |

模板不包含“客户等级”列。客户等级按现有规则自动计算：

1. Level A：X、Y、Z 都大于等于 60。
2. Level B：X、Y、Z 中至少两项大于等于 60。
3. Level C：X 大于等于 60。
4. Level D：其他情况。

## 导入规则

### 匹配规则

以“客户名称”做精确匹配：

1. 如果系统中存在同名客户，则更新该客户。
2. 如果系统中不存在同名客户，则创建新客户。
3. 客户名称导入前后去除首尾空格。

先采用精确匹配，避免模糊匹配误更新错误客户。后续如果业务需要，可以再单独设计“模糊匹配预览”。

### 更新规则

Excel 中每一行作为一条客户记录处理。更新已有客户时，模板中的字段会覆盖系统中对应字段。

空值处理规则：

1. 必填字段为空：跳过该行并记录错误。
2. 非必填字段为空：更新为空值。
3. 潜在贡献为空：保存为空值。

### 数据校验

导入时需要校验：

1. 文件类型必须是 `.xlsx`。
2. 第一行必须包含所有模板表头。
3. 客户名称、业务模式、区域、城市、X/Y/Z 评分不能为空。
4. 业务模式必须是 `Hunting` 或 `Farming`。
5. X/Y/Z 评分必须是 0-100 的数字。
6. 潜在贡献如果填写，必须是数字。
7. 完全空白的数据行跳过，不计入错误。

## 后端设计

在 `CustomerViewSet` 上新增两个 action：

1. `GET /api/customers/import-template/`
   - 返回 `docs/templates/customer_import_template.xlsx`。
   - 下载文件名建议为 `customer_import_template.xlsx`。

2. `POST /api/customers/import/`
   - 使用 `multipart/form-data` 上传文件，字段名为 `file`。
   - 解析第一个 Sheet。
   - 按模板表头读取每一行。
   - 校验并新增或更新客户。
   - 返回导入结果。

返回结构建议：

```json
{
  "created": 3,
  "updated": 5,
  "skipped": 2,
  "errors": [
    {
      "row": 4,
      "customer_name": "示例客户",
      "reason": "业务模式必须是 Hunting 或 Farming"
    }
  ]
}
```

后端可以新增小型工具函数，避免把导入解析逻辑全部堆在 action 内：

1. `_read_customer_import_rows(upload)`
2. `_parse_required_text(row, column)`
3. `_parse_score(value, column)`
4. `_parse_optional_decimal(value, column)`
5. `_calculate_customer_level(score_x, score_y, score_z)`
6. `_create_customer_import_template()`

## 前端设计

在客户列表页现有工具栏中增加两个按钮：

1. “下载模板”
   - 调用 `GET /api/customers/import-template/`。
   - 下载 `customer_import_template.xlsx`。

2. “导入客户”
   - 打开隐藏的文件选择框。
   - 只接受 `.xlsx`。
   - 调用 `POST /api/customers/import/`。
   - 导入成功后刷新客户列表。
   - 用消息提示展示新增、更新、跳过数量。

前端 API 文件 `frontend/src/api/customer.js` 新增：

1. `downloadCustomerImportTemplate()`
2. `importCustomers(file)`

## 错误处理

后端返回 400 的场景：

1. 未上传文件。
2. 文件后缀不是 `.xlsx`。
3. 文件无法被 `openpyxl` 读取。
4. 缺少模板表头。

单行数据错误不终止整个导入，只跳过该行并加入 `errors`。为了避免响应过大，错误列表最多返回前 50 条。

前端展示策略：

1. 整体文件错误：直接弹出错误消息。
2. 部分行错误：显示“导入完成：新增 X，更新 Y，跳过 Z”。
3. 如果需要查看具体错误，后续可再增加导入结果弹窗；本次先返回数据并在控制台保留完整响应。

## 测试计划

后端测试：

1. 下载模板接口返回 `.xlsx`，且表头与设计字段一致。
2. 上传模板格式的 Excel，能创建新客户。
3. 上传同名客户，能更新已有客户。
4. 评分导入后自动计算客户等级。
5. 缺少必填字段时跳过该行并返回错误。
6. 非法业务模式、非法评分、非法潜在贡献会跳过对应行。
7. 完全空白行会被忽略。

前端验证：

1. 客户列表页能下载模板。
2. 客户列表页能选择 `.xlsx` 文件上传。
3. 导入完成后客户列表刷新。
4. 上传失败时显示后端返回的错误信息。

## 实施顺序

1. 先写后端测试，覆盖模板下载和客户导入核心行为。
2. 实现模板生成/保存。
3. 实现客户导入解析和校验。
4. 增加客户导入 API 封装。
5. 在客户列表页增加下载模板和导入客户按钮。
6. 运行后端测试和前端构建。

## 待确认点

1. 更新已有客户时，Excel 中的空白非必填字段是否允许覆盖系统原值为空。当前设计是允许覆盖。
2. 客户名称是否必须精确匹配才更新。当前设计是精确匹配，避免误更新。
3. 导入结果错误明细本次是否只返回给接口，不做前端弹窗详情。当前设计是先不做详情弹窗。

