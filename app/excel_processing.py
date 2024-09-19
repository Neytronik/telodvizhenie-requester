import pandas as pd

from app.logger import logger


class Composer:

    def __init__(self, min_model_count, max_model_count, min_section_count, max_sections_count, reverse_order) -> None:
        super().__init__()
        self.reverse_order = reverse_order
        self.min_section_count = min_section_count
        self.max_sections_count = max_sections_count
        self.min_model_count = min_model_count
        self.max_model_count = max_model_count

    # Функция для разбивки записей
    def split_big_quantity(self, df_data):

        def split_rows(input_row, max_quantity_bound=self.max_model_count):
            rows = []
            quantity = input_row['Количество']
            split_id = 1
            while quantity > 2 * max_quantity_bound:
                new_row = input_row.copy()
                new_row['Количество'] = max_quantity_bound
                new_row['split_id'] = f"{split_id}"
                rows.append(new_row)
                quantity -= max_quantity_bound
                split_id += 1
            if quantity > 0:
                new_row = input_row.copy()
                new_row['Количество'] = quantity
                new_row['split_id'] = f"{split_id}"
                rows.append(new_row)
            return rows

        # Применение функции к каждой строке DataFrame
        new_rows = []
        for _, row in df_data.iterrows():
            new_rows.extend(split_rows(row))

        # Создание нового DataFrame из разбитых записей
        new_df = pd.DataFrame(new_rows)
        new_df.reset_index(drop=True, inplace=True)

        return new_df

    def sorting_data(self, df_data, split=True):
        if df_data.empty:
            return pd.DataFrame(), df_data

        if split:
            df_data = self.split_big_quantity(df_data)

        # Группировка и объединение товаров с одинаковыми артикулом и размером
        df_data = df_data.groupby(['Цвет', 'Артикул', 'Размер', "split_id"], as_index=False).agg({
            'Количество': 'sum',
        })

        # Добавляем колонку Сумма_Количество
        df_data = df_data.assign(
            Сумма_Количество=df_data.groupby(['Артикул', 'Размер', 'split_id'])['Количество'].transform('sum')
        )

        # Фильтруем данные
        df_filtered = df_data[df_data['Количество'] > 0]
        df_filtered = df_filtered[df_filtered['Сумма_Количество'] >= self.min_model_count]

        if df_filtered.empty:
            return pd.DataFrame(), df_data

        # Сортируем данные по общей сумме количества, цвету и ['Артикул', 'Размер']
        df_filtered = df_filtered.sort_values(
            by=['Сумма_Количество', 'Артикул', 'Размер', 'Цвет', 'split_id', 'Количество'],
            ascending=[True, False, False, False, True, True])

        # Берем первую связку артикул+размер
        first_artikul_razmer = df_filtered[['Артикул', 'Размер', 'split_id']].iloc[0]

        # Берем все цвета из этой выборки
        first_colors = df_filtered[(df_filtered['Артикул'] == first_artikul_razmer['Артикул']) &
                                   (df_filtered['Размер'] == first_artikul_razmer['Размер']) &
                                   (df_filtered['split_id'] == first_artikul_razmer['split_id'])]['Цвет'].unique()

        # Фильтруем таблицу, оставляя только те артикулы+размеры, которые подходят под выбранные цвета
        df_filtered = df_filtered[df_filtered['Цвет'].isin(first_colors)].copy()

        # Пересчитываем Сумма_Количество для отфильтрованного DataFrame
        df_filtered = df_filtered.assign(
            Сумма_Количество=df_filtered.groupby(['Артикул', 'Размер', 'split_id'])['Количество'].transform('sum')
        )

        # Фильтруем данные снова
        df_filtered = df_filtered[df_filtered['Сумма_Количество'] >= self.min_model_count]

        # Сортируем данные по общей сумме количества, цвету и ['Артикул', 'Размер']
        df_filtered = df_filtered.sort_values(
            by=['Сумма_Количество', 'Артикул', 'Размер', 'Цвет', 'split_id', 'Количество'],
            ascending=[True, False, False, False, True, True])

        # тут логика определения не включенных позиций
        # Создаем DataFrame для хранения остатков
        remaining_df = df_data[~df_data.index.isin(df_filtered.index)]

        return df_filtered, remaining_df

    def select_rows(self, color, first_quantity, all_quantity_sum, df_data, processed_quantities=None):
        if processed_quantities is None:
            processed_quantities = []

        selected_rows = []
        df_same_color = df_data[df_data['Цвет'] == color]
        for index, row in df_same_color.iterrows():
            if (row['Количество'] >= first_quantity or row['Количество'] >= self.min_model_count
            ):
                selected_rows.append(row)
        if not selected_rows:
            return 0, []

        if len(selected_rows) < self.min_section_count:
            unique_quantities = df_same_color['Количество'].unique()
            unique_quantities = [q for q in unique_quantities if q not in processed_quantities]

            if not unique_quantities or len(unique_quantities) < 2:
                return first_quantity, []

            second_largest_quantity = sorted(unique_quantities)[-2]
            processed_quantities.append(second_largest_quantity)

            new_all_quantity_sum = all_quantity_sum - first_quantity + second_largest_quantity

            if new_all_quantity_sum >= self.min_model_count:
                return self.select_rows(color, second_largest_quantity, new_all_quantity_sum, df_data,
                                        processed_quantities)
            else:
                return first_quantity, []

        return first_quantity, selected_rows

    def selector_composer(self, df_data_composer, remaining_data_outer=None, split=True):
        if split:
            df_data_composer = self.split_big_quantity(df_data_composer)
        df_data, remaining_data = self.sorting_data(df_data_composer, split=False)
        if df_data.empty:
            if remaining_data_outer is not None:
                remaining_data = pd.concat([remaining_data, remaining_data_outer],
                                           ignore_index=False)
            return df_data, remaining_data
        if remaining_data_outer is not None:
            remaining_data = pd.concat([remaining_data, remaining_data_outer], ignore_index=False)
        # Шаг 1: Выбираем первый цвет и его количество
        first_row = df_data.iloc[0]
        artikul = first_row['Артикул']
        size = first_row['Размер']
        first_color = first_row['Цвет']
        first_split_id = first_row['split_id']
        df_same_artikul_size = df_data[
            (df_data['Артикул'] == artikul) & (df_data['Размер'] == size) & (df_data['split_id'] == first_split_id)]
        colors = df_same_artikul_size['Цвет'].unique()

        # Создаем пустой DataFrame для хранения всех выбранных строк
        df_all_selected = pd.DataFrame()

        minus_all_sum = 0
        for color in colors:
            df_same_artikul_size_color = df_data[
                (df_data['Артикул'] == artikul) & (df_data['Размер'] == size) & (df_data['Цвет'] == color) & (
                        df_data['split_id'] == first_split_id)]
            first_row = df_same_artikul_size_color.iloc[0]
            first_quantity = first_row['Количество']
            all_quantity_sum = first_row['Сумма_Количество'] - minus_all_sum
            min_filter_items_quantity, selected_rows = self.select_rows(color, first_quantity, all_quantity_sum,
                                                                        df_data)
            if selected_rows:
                minus_all_sum += min_filter_items_quantity
                df_all_selected = pd.concat([df_all_selected, pd.DataFrame(selected_rows)], ignore_index=False)

            # Если сумма меньше 120, удаляем модель целиком и вызываем функцию снова
        if minus_all_sum < self.min_model_count:
            df_data = df_data_composer[
                ~((df_data_composer['Артикул'] == artikul) &
                  (df_data_composer['Размер'] == size) &
                  (df_data_composer['Цвет'] == first_color) &
                  (df_data_composer['split_id'] == first_split_id)
                  )]
            df_data_composer_remaining = df_data_composer[
                ((df_data_composer['Артикул'] == artikul) &
                 (df_data_composer['Размер'] == size) &
                 (df_data_composer['Цвет'] == first_color) &
                 (df_data_composer['split_id'] == first_split_id)
                 )
            ]
            if remaining_data_outer is not None:
                df_data_composer_remaining = pd.concat([df_data_composer_remaining, remaining_data_outer],
                                                       ignore_index=False)
            return self.selector_composer(df_data, df_data_composer_remaining, False)

        # Находим пересечения артикулов и размеров для всех цветов
        artikul_size_sets = []
        remaining_colors = []
        for color in colors:
            df_same_color = df_all_selected[df_all_selected['Цвет'] == color]
            artikul_size_set = set(zip(df_same_color['Артикул'], df_same_color['Размер'], df_same_color['split_id']))
            if artikul_size_set:
                artikul_size_sets.append(artikul_size_set)
                remaining_colors.append(color)

        # Пересечение всех множеств артикулов и размеров
        common_artikul_size = set.intersection(*artikul_size_sets)
        if len(common_artikul_size) < self.min_section_count:
            df_data = df_data_composer[
                ~((df_data_composer['Артикул'] == artikul) &
                  (df_data_composer['Размер'] == size) &
                  (df_data_composer['Цвет'] == first_color) &
                  (df_data_composer['split_id'] == first_split_id)
                  )]
            df_data_composer_remaining = df_data_composer[
                ((df_data_composer['Артикул'] == artikul) &
                 (df_data_composer['Размер'] == size) &
                 (df_data_composer['Цвет'] == first_color) &
                 (df_data_composer['split_id'] == first_split_id)
                 )
            ]
            if remaining_data_outer is not None:
                df_data_composer_remaining = pd.concat([df_data_composer_remaining, remaining_data_outer],
                                                       ignore_index=False)

            return self.selector_composer(df_data, df_data_composer_remaining, False)

        # Создаем пустой DataFrame для хранения итогового результата
        df_final_selected = pd.DataFrame()

        # Фильтруем df_filtered по найденным пересечениям
        for artikul, size, split_id in common_artikul_size:
            df_filtered_subset = df_all_selected[
                (df_all_selected['Артикул'] == artikul) & (df_all_selected['Размер'] == size) & (
                        df_all_selected['split_id'] == split_id) & (
                    df_all_selected['Цвет'].isin(remaining_colors))]
            df_final_selected = pd.concat([df_final_selected, df_filtered_subset], ignore_index=False)

        # Удаляем дубликаты, если они есть
        df_final_selected = df_final_selected.drop_duplicates()

        # Определяем остатки, которые не попали в итоговый выбор
        remaining_df = df_data[~df_data.index.isin(df_final_selected.index)]

        # Сортируем итоговый результат
        data, remaining_df_sorted = self.sorting_data(df_final_selected, False)

        # Объединяем все остатки
        remaining_df_selected = pd.concat([remaining_df, remaining_df_sorted, remaining_data], ignore_index=False)
        remaining_df_selected = remaining_df_selected.drop(columns=['Сумма_Количество'])
        return data, remaining_df_selected

    def slice_layers(self, df_items, remaining_data=None):
        layers = []
        if df_items.empty:
            return layers, remaining_data
        remaining_df = df_items.copy()
        remaining_df.reset_index(drop=True, inplace=True)
        colors = df_items['Цвет'].unique()
        max_quantity_in_section = self.max_model_count

        for color in colors:
            df_color = remaining_df[remaining_df['Цвет'] == color].copy()
            # df_color = df_color.sort_values(by='Артикул')  # Сортируем по полю "Артикул"
            min_quantity = min(df_color['Количество'].min(), max_quantity_in_section)  # Добавление верхней границы 250
            max_quantity_in_section -= min_quantity
            if min_quantity <= 0:
                break
            # Нарезаем слой для текущего цвета
            layer = df_color.head(self.max_sections_count).copy()  # Берем первые max_sections записей
            layer['Количество'] = min_quantity
            layers.append(layer)

            # Уменьшаем количество только в первых max_sections записях
            indices_to_update = df_color.head(self.max_sections_count).index
            remaining_df.loc[indices_to_update, 'Количество'] -= min_quantity
            remaining_df = remaining_df[remaining_df['Количество'] > 0]

            # Ограничиваем число секций до max_sections
            if len(layers) >= self.max_sections_count:
                break

        remaining_df_sliced = remaining_df
        if remaining_data is not None:
            remaining_df_sliced = pd.concat([remaining_df, remaining_data], ignore_index=True)

        remaining_df_sliced = remaining_df_sliced.groupby(['Цвет', 'Артикул', 'Размер', ], as_index=False).agg({
            'Количество': 'sum',
        })
        remaining_df_sliced.reset_index(drop=True, inplace=True)
        remaining_df_sliced = remaining_df_sliced[remaining_df_sliced['Количество'] > 0]

        return layers, remaining_df_sliced

    def create_order(self, layers_for_order, ):
        order = pd.DataFrame()

        for layer in layers_for_order:
            color = layer['Цвет'].iloc[0]
            artikul_size = layer.apply(lambda row: f"{row['Артикул']}_{row['Размер']}___{row['split_id']}", axis=1)
            quantities = [layer['Количество'].iloc[0]] * self.max_sections_count

            # Убедимся, что длина массивов совпадает
            min_length = min(self.max_sections_count, len(layer))

            # Создаем DataFrame для текущего слоя
            df_layer = pd.DataFrame({
                'Цвет': [color] * min_length,
                'Артикул_Размер': artikul_size[:min_length],
                'Количество': quantities[:min_length]
            })

            # Добавляем текущий слой в заявку
            order = pd.concat([order, df_layer], ignore_index=True)

        # Подсчитываем общую сумму количеств
        total_quantity = order['Количество'].sum()

        # Добавляем строку с общей суммой количеств
        total_row = pd.DataFrame({
            'Цвет': ['ИТОГ'],
            'Артикул_Размер': [''],
            'Количество': [total_quantity]
        })

        order = pd.concat([order, total_row], ignore_index=True)

        return order

    def save_orders_to_excel(self, orders_to_excel, file_path="../orders.xlsx"):
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            for i, order in enumerate(orders_to_excel):
                order_sheet_name = f'Order_{i + 1}'
                logger.print(f'Creating: {order_sheet_name}')
                # Преобразуем DataFrame с помощью pivot
                pivot_order = order.pivot(index='Цвет', columns='Артикул_Размер', values='Количество').reset_index()
                # Записываем DataFrame на соответствующий лист
                pivot_order.to_excel(writer, sheet_name=order_sheet_name, index=False)
