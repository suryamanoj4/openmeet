interface GraphQLResult<TData> {
	data?: TData;
	error?: { message: string };
}

export function requireMutationResult<
	TValue,
	TKey extends string
>(
	result: GraphQLResult<Partial<Record<TKey, TValue>>>,
	key: TKey,
	fallbackMessage: string
): TValue {
	if (result.error) {
		throw new Error(result.error.message);
	}

	const value = result.data?.[key];
	if (value === undefined || value === null) {
		throw new Error(fallbackMessage);
	}

	return value;
}
